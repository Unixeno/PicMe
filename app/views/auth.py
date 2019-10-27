from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from flask import session
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import Email, DataRequired, Length


bp = Blueprint('auth', __name__, url_prefix='/auth')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8)])

    @staticmethod
    def validate_email(form, field):
        user = User()
        if user.user_exist(field.data):
            raise ValidationError('邮箱已被注册')


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


@bp.route('/')
def index():
    return redirect(url_for('.login'))


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        form = LoginForm()
        if form.validate():
            user = User()
            user_id = user.login(form.email.data, form.password.data)
            if user_id:
                session['user_id'] = user_id
                return jsonify({'err': 0})
            return jsonify({'err': 1, 'info': '用户名或密码不正确'})
    else:
        return render_template('auth/login.html')


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        form = RegisterForm()
        if form.validate():
            user = User()
            user.register(email=form.email.data, password=form.password.data)
            return jsonify({'err': 0})
    else:
        return render_template('auth/register.html')


@bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('.login'))
