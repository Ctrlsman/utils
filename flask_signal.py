import flask_login
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import redirect, url_for

app = Flask(__name__)


class Config:
    HTTP_HOST = '0.0.0.0'
    HTTP_PORT = 9965
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/test?charset=utf8mb4'
    DEBUG = 1
    SECRET_KEY = '!@#456&*&('


app.config.from_object(Config)
db = SQLAlchemy()
db.init_app(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(id):
    user = User.query.get(id)
    return user


password = '123'


class User(flask_login.UserMixin, db.Model):
    __tablename__ = 'login_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(128), nullable=False)
    login_count = db.Column(db.Integer, default=0)
    last_login_ip = db.Column(db.String(128), default='Unknown')


db.create_all(app=app)


@flask_login.user_logged_in.connect_via(app)
def _track_logins(sender, user, **extra):
    user.login_count += 1
    user.last_login_ip = request.remote_addr
    db.session.commit()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
        <form action='login' method='POST'>
            <input type='text' name='name' id='name' placeholder='name'></input>
            <input type='password' name='pw' id='pw' placeholder='name'></input>
            <input type='submit' name='submit' ></input>
        </form>
        '''
    name = request.form.get('name')
    pw = request.form.get('pw')
    if pw == '123':
        user = User.query.filter_by(name=name).first()
        if not user:
            user = User()
            user.name = name
            db.session.add(user)
            db.session.commit()
        flask_login.login_user(user)
        return redirect(url_for('protected'))
    return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
    user = flask_login.current_user
    return 'Logged in as: {}| Login_count: {} | IP: {}'.format(user.name, user.login_count, user.last_login_ip)


if __name__ == '__main__':
    app.run()
