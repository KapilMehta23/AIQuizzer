from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    from app.routes import auth, quiz
    app.register_blueprint(auth.bp)
    app.register_blueprint(quiz.bp)

    with app.app_context():
        db.create_all()

    return app


# ena badle if I type this:
# from sqlalchemy import inspect
# from sqlalchemy import inspect, text
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# def print_tables_and_data():
#     inspector = inspect(db.engine)
#     tables = inspector.get_table_names()
    
#     print("Available tables and their contents:")
#     for table_name in tables:
#         print(f"\n{table_name}:")
        
#         # Print column information
#         columns = inspector.get_columns(table_name)
#         print("Columns:")
#         for column in columns:
#             print(f"  - {column['name']} ({column['type']})")
        
#         # Print table data
#         print("\nData:")
#         query = text(f"SELECT * FROM {table_name}")
#         result = db.session.execute(query)
        
#         # Print column headers
#         headers = result.keys()
#         print("  |  ".join(headers))
#         print("-" * (len(headers) * 15))  # Separator line
        
#         # Print rows
#         for row in result:
#             print("  |  ".join(str(value) for value in row))
        
#         print("\n" + "="*50)  # Separator between tables

# if _name_ == '_main_':
#     with app.app_context():
#         print_tables_and_data()