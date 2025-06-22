# config.py

class Config:
    SECRET_KEY = "your-very-secret-freelance-key"

    # MySQL Database Configuration
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "Pucrs2025"  # Use your MySQL password
    MYSQL_DB = "demand_tracker"  # The database you created

    # File Upload Configuration
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'docx', 'zip', 'rar'}