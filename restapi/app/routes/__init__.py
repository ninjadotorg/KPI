import requests
import json
import base64

from flask import request, g
from werkzeug.security import generate_password_hash
from app import db
from app.helpers.response import response_ok, response_error
from app.routes.handshake import handshake_routes
from app.routes.event import event_routes
from app.routes.user import user_routes
from app.routes.match import match_routes
from app.routes.outcome import outcome_routes
from app.routes.setting import setting_routes
from app.routes.admin import admin_routes
from app.routes.category import category_routes
from app.routes.source import source_routes
from app.routes.tx import tx_routes
from app.routes.token import token_routes
from app.routes.contract import contract_routes
from app.routes.hook import hook_routes
from app.routes.redeem import redeem_routes
from app.routes.referral import referral_routes
from flask_jwt_extended import (jwt_required, create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_refresh_token_required)


def init_routes(app):
    @app.route('/')
    def hello():
        return 'Cryptosign API'

    app.register_blueprint(handshake_routes, url_prefix='/handshake')
    app.register_blueprint(event_routes, url_prefix='/event')
    app.register_blueprint(match_routes, url_prefix='/match')
    app.register_blueprint(outcome_routes, url_prefix='/outcome')
    app.register_blueprint(setting_routes, url_prefix='/setting')
    app.register_blueprint(tx_routes, url_prefix='/tx')
    app.register_blueprint(admin_routes, url_prefix='/admin')
    app.register_blueprint(category_routes, url_prefix='/category')
    app.register_blueprint(source_routes, url_prefix='/source')
    app.register_blueprint(token_routes, url_prefix='/token')
    app.register_blueprint(contract_routes, url_prefix='/contract')
    app.register_blueprint(hook_routes, url_prefix='/hook')
    app.register_blueprint(redeem_routes, url_prefix='/redeem')
    app.register_blueprint(referral_routes, url_prefix='/referral')
    app.register_blueprint(user_routes)
