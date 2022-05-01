from flask import render_template
from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/error.html'), 404


@bp.app_errorhandler(413)
def not_found_error(error):
    return render_template('errors/error.html'), 413


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/error.html'), 500
