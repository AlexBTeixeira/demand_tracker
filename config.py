# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # A chave secreta será lida da variável de ambiente no Render.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'uma-chave-secreta-para-desenvolvimento-local')

    # Configuração do Banco de Dados MySQL lida das variáveis de ambiente.
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'bs9ttstmwbpyexuox7iu-mysql.services.clever-cloud.com')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'upltb1hqgecsy3v1')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'DEZgzvawJo6QEQ3zvklC')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'bs9ttstmwbpyexuox7iu')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '257982993797372')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', 'mflOkv9g8GE5eea2N5Gh3e0kv9A')
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dccj3u9nq')
    MYSQL_CURSORCLASS = 'DictCursor' # Adicionado aqui para centralizar a configuração.

    # Configuração de Upload de Arquivos
    # AVISO: O sistema de arquivos do Render é efêmero. Uploads serão perdidos em reinicializações.
    # A solução permanente é usar um serviço de armazenamento como o AWS S3.
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'docx', 'zip', 'rar'}