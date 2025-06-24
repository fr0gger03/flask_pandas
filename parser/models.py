from parser.app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users_tb'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(180), nullable=False)
    
    # Relationship: One user can have many projects
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    __tablename__ = 'projects_tb'
    pid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users_tb.id'), nullable=False)
    projectname = db.Column(db.String(20), nullable=False, unique=True)
    
    # Relationship: One project can have many workloads
    workloads = db.relationship('Workload', backref='project', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.projectname}>'


class Workload(db.Model):
    __tablename__ = 'workloads_tb'
    vmid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('projects_tb.pid'), nullable=False)
    mobid = db.Column(db.String(20))
    cluster = db.Column(db.String(40))
    virtualdatacenter = db.Column(db.String(40))
    os = db.Column(db.String(40))
    os_name = db.Column(db.String(40))
    vmstate = db.Column(db.String(20))
    vcpu = db.Column(db.Integer)
    vmname = db.Column(db.String(40))
    vram = db.Column(db.Integer)
    ip_addresses = db.Column(db.String(60))
    vinfo_provisioned = db.Column(db.Numeric(12,6))
    vinfo_used = db.Column(db.Numeric(12,6))
    vmdktotal = db.Column(db.Numeric(12,6))
    vmdkused = db.Column(db.Numeric(12,6))
    readiops = db.Column(db.Numeric(12,6))
    writeiops = db.Column(db.Numeric(12,6))
    peakreadiops = db.Column(db.Numeric(12,6))
    peakwriteiops = db.Column(db.Numeric(12,6))
    readthroughput = db.Column(db.Numeric(12,6))
    writethroughput = db.Column(db.Numeric(12,6))
    peakreadthroughput = db.Column(db.Numeric(12,6))
    peakwritethroughput = db.Column(db.Numeric(12,6))

    def __repr__(self):
        return f'<Workload {self.vmname}>'

    @property
    def total_storage_gb(self):
        """Calculate total storage in GB."""
        return float(self.vmdktotal) if self.vmdktotal else 0.0
    
    @property
    def used_storage_gb(self):
        """Calculate used storage in GB."""
        return float(self.vmdkused) if self.vmdkused else 0.0
    
    @property
    def storage_utilization_percent(self):
        """Calculate storage utilization percentage."""
        if self.vmdktotal and float(self.vmdktotal) > 0:
            return round((float(self.vmdkused) / float(self.vmdktotal)) * 100, 2)
        return 0.0
