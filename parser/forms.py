from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import InputRequired, Length, ValidationError

from parser.models import User

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

    submit = SubmitField('Create Project')

class CreateWorkloadForm(FlaskForm):

    # mobid = db.Column(db.String(20))
    # cluster = db.Column(db.String(40))
    # virtualdatacenter = db.Column(db.String(40))
    # os = db.Column(db.String(40))
    # os_name = db.Column(db.String(40))
    # vmstate = db.Column(db.String(20))
    # vcpu = db.Column(db.Integer)
    # vmname = db.Column(db.String(40))
    # vram = db.Column(db.Integer)
    # ip_addresses = db.Column(db.String(60))
    # vinfo_provisioned = db.Column(db.Numeric(12,6))
    # vinfo_used = db.Column(db.Numeric(12,6))
    # vmdktotal = db.Column(db.Numeric(12,6))
    # vmdkused = db.Column(db.Numeric(12,6))
    # readiops = db.Column(db.Numeric(12,6))
    # writeiops = db.Column(db.Numeric(12,6))
    # peakreadiops = db.Column(db.Numeric(12,6))
    # peakwriteiops = db.Column(db.Numeric(12,6))
    # readthroughput = db.Column(db.Numeric(12,6))
    # writethroughput = db.Column(db.Numeric(12,6))
    # peakreadthroughput = db.Column(db.Numeric(12,6))
    # peakwritethroughput = db.Column(db.Numeric(12,6))

    submit = SubmitField('Create Workload')

class UploadFileForm(FlaskForm):
    file = FileField('excel file', validators=[
        FileRequired(),
        FileAllowed(['xls','xlsx'], 'Excel files only!')
    ])  
    submit = SubmitField('Upload File')

