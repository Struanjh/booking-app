from flask import Blueprint, render_template
from app import db

errors_bp = Blueprint('errors_bp', __name__, template_folder="templates/errors")

@errors_bp.app_errorhandler(404)
def fileNotFoundError(error):
    return render_template('404.html'), 404

@errors_bp.app_errorhandler(500)
def internalError(error):
    db.session.rollback()
    return render_template('500.html'), 500


