from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    userid = IntegerField('Userid', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    
