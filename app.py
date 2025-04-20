import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from app.modules.nginx_manager import NginxManager
from app.modules.config_validator import ConfigValidator
from app.routes.auth import auth_bp, login_required

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['NGINX_CONFIG_DIR'] = '/etc/nginx' # Change this to actual nginx directory

nginx_manager = NginxManager(app.config['NGINX_CONFIG_DIR'])
config_validator = ConfigValidator()

# Store these objects in app.config for easy access in routes
app.config['NGINX_MANAGER'] = nginx_manager
app.config['CONFIG_VALIDATOR'] = config_validator

from app.routes.main import main_bp
from app.routes.configs import configs_bp
from app.routes.sites import sites_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(configs_bp, url_prefix='/configs')
app.register_blueprint(sites_bp, url_prefix='/sites')

# Protect all routes with login_required
@app.before_request
def check_auth():
    if request.endpoint and not request.endpoint.startswith('auth.') and \
       not request.endpoint.startswith('static'):
        return login_required(lambda: None)()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 