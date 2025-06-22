# blueprints/demands.py
import os
from flask import Blueprint, render_template, request, jsonify, flash, current_app, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import MySQLdb.cursors
from extensions import mysql

demands_bp = Blueprint('demands', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@demands_bp.route('/')
def dashboard():
    view = request.args.get('view', 'prioritize') # 'prioritize' or 'all'
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    query_base = "SELECT id, title, status, created_at, priority, executed_hours, estimated_hours FROM demands"
    
    if view == 'prioritize':
        query = f"{query_base} WHERE status IN ('Em Fila', 'Em Execução') ORDER BY priority ASC, created_at ASC"
    else: # 'all'
        query = f"{query_base} ORDER BY created_at DESC"
        
    cur.execute(query)
    demands = cur.fetchall()
    cur.close()

    return render_template('pages/demands/dashboard.html', demands=demands, current_view=view)

@demands_bp.route('/<int:demand_id>')
def detail(demand_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if demand_id == 0: # Indicates a new demand
        demand = None
        attachments = []
        work_history = []
    else:
        cur.execute("SELECT * FROM demands WHERE id = %s", (demand_id,))
        demand = cur.fetchone()

        if not demand:
            flash('Demanda não encontrada.', 'danger')
            return redirect(url_for('demands.dashboard'))
            
        cur.execute("SELECT id, filename, filepath FROM attachments WHERE demand_id = %s", (demand_id,))
        attachments = cur.fetchall()
        
        cur.execute("""
            SELECT wl.*, ws.start_time, ws.end_time 
            FROM work_logs wl
            JOIN work_sessions ws ON wl.work_session_id = ws.id
            WHERE wl.demand_id = %s
            ORDER BY ws.start_time DESC
        """, (demand_id,))
        work_history = cur.fetchall()

    cur.close()
    
    return render_template('pages/demands/detail.html', demand=demand, attachments=attachments, work_history=work_history)

@demands_bp.route('/save', methods=['POST'])
def save_demand():
    demand_id = request.form.get('demand_id')
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status')
    estimated_hours = request.form.get('estimated_hours') or None

    if not title or not status:
        flash('Título e Status são campos obrigatórios.', 'danger')
        return redirect(url_for('demands.dashboard'))

    conn = mysql.connection
    cur = conn.cursor()

    try:
        if demand_id and demand_id != '0': # Update existing demand
            cur.execute("""
                UPDATE demands SET title=%s, description=%s, status=%s, estimated_hours=%s, updated_at=NOW()
                WHERE id=%s
            """, (title, description, status, estimated_hours, demand_id))
            flash('Demanda atualizada com sucesso!', 'success')
            redirect_url = url_for('demands.detail', demand_id=demand_id)
        else: # Create new demand
            cur.execute("SELECT COALESCE(MAX(priority), -1) FROM demands")
            max_priority = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO demands (title, description, status, estimated_hours, priority)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, description, status, estimated_hours, max_priority + 1))
            demand_id = cur.lastrowid
            flash('Demanda criada! Agora, defina sua prioridade.', 'info')
            redirect_url = url_for('demands.prioritize', new_demand_id=demand_id) # Redirect to prioritization

        # Handle file uploads for both create and update
        if 'attachments' in request.files:
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'demands', str(demand_id))
            os.makedirs(upload_path, exist_ok=True)
            
            for file in request.files.getlist('attachments'):
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_path, filename)
                    file.save(filepath)
                    
                    relative_path = os.path.join('demands', str(demand_id), filename).replace('\\', '/')
                    cur.execute(
                        "INSERT INTO attachments (demand_id, filename, filepath) VALUES (%s, %s, %s)",
                        (demand_id, filename, relative_path)
                    )

        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao salvar demanda: {e}', 'danger')
        redirect_url = url_for('demands.dashboard')
    finally:
        cur.close()

    return redirect(redirect_url)

@demands_bp.route('/prioritize/<int:new_demand_id>')
def prioritize(new_demand_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT id, title, status, priority FROM demands WHERE status IN ('Em Fila', 'Em Execução') ORDER BY priority ASC, created_at ASC"
    cur.execute(query)
    demands = cur.fetchall()
    cur.close()

    return render_template('pages/demands/prioritize.html', demands=demands, new_demand_id=new_demand_id)

@demands_bp.route('/attachment/<int:attachment_id>')
def download_attachment(attachment_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT filename, filepath FROM attachments WHERE id = %s", (attachment_id,))
    attachment = cur.fetchone()
    cur.close()
    
    if not attachment:
        return "Arquivo não encontrado", 404
        
    return send_from_directory(
        directory=current_app.config['UPLOAD_FOLDER'],
        path=attachment['filepath'],
        download_name=attachment['filename'],
        as_attachment=True
    )
    
@demands_bp.route('/update_priorities', methods=['POST'])
def update_priorities():
    data = request.get_json()
    ordered_ids = data.get('ordered_ids')

    if not ordered_ids or not isinstance(ordered_ids, list):
        return jsonify(status="error", message="Lista de IDs inválida."), 400

    conn = mysql.connection
    cur = conn.cursor()
    try:
        # Update priority for each demand in a single transaction
        for index, demand_id in enumerate(ordered_ids):
            cur.execute("UPDATE demands SET priority = %s WHERE id = %s", (index, demand_id))
        conn.commit()
        return jsonify(status="success", message="Prioridades atualizadas."), 200
    except Exception as e:
        conn.rollback()
        return jsonify(status="error", message=f"Erro ao atualizar prioridades: {e}"), 500
    finally:
        cur.close()