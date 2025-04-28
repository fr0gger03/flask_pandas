from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import InputRequired, Length, ValidationError

from models import User

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

class CreateProjectForm(FlaskForm):
    project_name = StringField(validators=[
                                InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Project Name"})

    project_description = StringField(validators=[
                                      InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Project Description"})

    submit = SubmitField('Create Project')

class CreateWorkloadForm(FlaskForm):
    workload_name = StringField(validators=[
                                 InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Workload Name"})

    workload_description = StringField(validators=[
                                       InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Workload Description"})

    submit = SubmitField('Create Workload')

class UploadFileForm(FlaskForm):
    file = FileField('excel file', validators=[
        FileRequired(),
        FileAllowed(['xls','xlsx'], 'Excel files only!')
    ])  
    submit = SubmitField('Upload File')

