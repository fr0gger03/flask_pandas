from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DecimalField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import InputRequired, Length, ValidationError, Optional

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
    projectname = StringField(validators=[
                                InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Project Name"})

    submit = SubmitField('Create Project')

    def validate_projectname(self, projectname):
        from parser.models import Project
        existing_project = Project.query.filter_by(
            projectname=projectname.data).first()
        if existing_project:
            raise ValidationError(
                'That project name already exists. Please choose a different one.')

class EditProjectForm(FlaskForm):
    projectname = StringField(validators=[
                                InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Project Name"})

    submit = SubmitField('Update Project')

    def __init__(self, original_projectname, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_projectname = original_projectname

    def validate_projectname(self, projectname):
        if projectname.data != self.original_projectname:
            from parser.models import Project
            existing_project = Project.query.filter_by(
                projectname=projectname.data).first()
            if existing_project:
                raise ValidationError(
                    'That project name already exists. Please choose a different one.')

class CreateWorkloadForm(FlaskForm):
    # Basic VM Information
    vmname = StringField('VM Name', validators=[
        InputRequired(), Length(min=1, max=100)], render_kw={"placeholder": "VM Name"})
    
    mobid = StringField('MOB ID', validators=[
        Length(max=50)], render_kw={"placeholder": "VMware Managed Object ID"})
    
    os = StringField('Operating System', validators=[
        Length(max=120)], render_kw={"placeholder": "e.g., Windows Server 2019"})
    
    os_name = StringField('Hostname', validators=[
        Length(max=100)], render_kw={"placeholder": "e.g., web-server-01"})
    
    vmstate = SelectField('VM State', choices=[
        ('poweredOn', 'Powered On'),
        ('poweredOff', 'Powered Off'),
        ('suspended', 'Suspended')
    ], default='poweredOn')
    
    # Resource Allocation
    vcpu = IntegerField('vCPUs', validators=[
        InputRequired()], render_kw={"placeholder": "Number of vCPUs", "min": "1"})
    
    vram = IntegerField('vRAM (MB)', validators=[
        InputRequired()], render_kw={"placeholder": "Memory in MB", "min": "512"})
    
    # Infrastructure Information
    cluster = StringField('Cluster', validators=[
        Length(max=100)], render_kw={"placeholder": "Cluster name"})
    
    virtualdatacenter = StringField('Datacenter', validators=[
        Length(max=100)], render_kw={"placeholder": "Datacenter name"})
    
    ip_addresses = StringField('IP Addresses', validators=[
        Length(max=255)], render_kw={"placeholder": "192.168.1.10, 10.0.0.5"})
    
    # Storage Information
    vinfo_provisioned = DecimalField('vInfo Provisioned (GB)', validators=[
        Optional()], render_kw={"placeholder": "Provisioned storage from vInfo", "step": "0.1", "min": "0"})
    
    vinfo_used = DecimalField('vInfo Used (GB)', validators=[
        Optional()], render_kw={"placeholder": "Used storage from vInfo", "step": "0.1", "min": "0"})
    
    vmdktotal = DecimalField('Total Storage (GB)', validators=[
        InputRequired()], render_kw={"placeholder": "Total storage in GB", "step": "0.1", "min": "0"})
    
    vmdkused = DecimalField('Used Storage (GB)', validators=[
        InputRequired()], render_kw={"placeholder": "Used storage in GB", "step": "0.1", "min": "0"})
    
    # Performance Metrics - IOPS
    readiops = DecimalField('Read IOPS', validators=[
        Optional()], render_kw={"placeholder": "Average read IOPS", "step": "0.1", "min": "0"})
    
    writeiops = DecimalField('Write IOPS', validators=[
        Optional()], render_kw={"placeholder": "Average write IOPS", "step": "0.1", "min": "0"})
    
    peakreadiops = DecimalField('Peak Read IOPS', validators=[
        Optional()], render_kw={"placeholder": "Peak read IOPS", "step": "0.1", "min": "0"})
    
    peakwriteiops = DecimalField('Peak Write IOPS', validators=[
        Optional()], render_kw={"placeholder": "Peak write IOPS", "step": "0.1", "min": "0"})
    
    # Performance Metrics - Throughput
    readthroughput = DecimalField('Read Throughput (MB/s)', validators=[
        Optional()], render_kw={"placeholder": "Average read throughput", "step": "0.1", "min": "0"})
    
    writethroughput = DecimalField('Write Throughput (MB/s)', validators=[
        Optional()], render_kw={"placeholder": "Average write throughput", "step": "0.1", "min": "0"})
    
    peakreadthroughput = DecimalField('Peak Read Throughput (MB/s)', validators=[
        Optional()], render_kw={"placeholder": "Peak read throughput", "step": "0.1", "min": "0"})
    
    peakwritethroughput = DecimalField('Peak Write Throughput (MB/s)', validators=[
        Optional()], render_kw={"placeholder": "Peak write throughput", "step": "0.1", "min": "0"})

    submit = SubmitField('Create Workload')

class EditWorkloadForm(CreateWorkloadForm):
    submit = SubmitField('Update Workload')

class UploadFileForm(FlaskForm):
    file = FileField('excel file', validators=[
        FileRequired(),
        FileAllowed(['xls','xlsx'], 'Excel files only!')
    ])  
    submit = SubmitField('Upload File')

