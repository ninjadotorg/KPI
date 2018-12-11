import requests
import json

from flask import request, g

from app.routes.user import user_routes
from app.routes.company import company_routes
from app.routes.people import people_routes
from app.routes.project import project_routes
from app.routes.team import team_routes
from app.routes.role import role_routes
from app.routes.review_type import type_routes
from app.routes.question import question_routes
from app.routes.answer import answer_routes


def init_routes(app):
    @app.route('/')
    def hello():
        return 'KPI API'

    app.register_blueprint(company_routes, url_prefix='/company')
    app.register_blueprint(people_routes, url_prefix='/people')
    app.register_blueprint(project_routes, url_prefix='/project')
    app.register_blueprint(team_routes, url_prefix='/team')
    app.register_blueprint(role_routes, url_prefix='/role')
    app.register_blueprint(type_routes, url_prefix='/type')
    app.register_blueprint(question_routes, url_prefix='/question')
    app.register_blueprint(answer_routes, url_prefix='/answer')
    app.register_blueprint(user_routes)
