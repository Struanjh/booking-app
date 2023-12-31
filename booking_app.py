import os
from app import create_app, db, cli
from app.models import User, Role, EnglishClasses

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role, 'EnglishClasses': EnglishClasses}


   