from flask import Flask
from flask_socketio import SocketIO
from flask_mail import Mail

socketio = SocketIO()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'ammadmughal567@gmail.com'
    app.config['MAIL_PASSWORD'] = 'xjka jqzt ocrq scnn'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    mail.init_app(app)
    socketio.init_app(app)

    from .main import main as main_blueprint
    from .authentication import authentication as authentication_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(authentication_blueprint)

    # Import and register the sockets
    from app import sockets

    return app
