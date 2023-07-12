
from flask import Flask 

app = Flask(__name__)

## placed at end to avoid circular imports -- routes needs access to app instance
from app import routes



