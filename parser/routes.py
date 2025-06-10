from flask import Blueprint, request, redirect, render_template, url_for, session
from flask import current_app as app
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user
from parser.app import db, bcrypt
from parser.forms import RegisterForm, LoginForm, UploadFileForm, CreateProjectForm, CreateWorkloadForm
from parser.models import User, Workload, Project

import os, sys
import pandas as pd
from parser.transform.data_validation import filetype_validation
from parser.transform.transform_lova import lova_conversion
from parser.transform.transform_rvtools import rvtools_conversion


bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    return render_template("pages/home.html")


@bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("pages/dashboard.html")


@bp.route("/create_project", methods=['GET', 'POST'])
@login_required
def create_project():
    return render_template("pages/create_project.html")


@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                if login_user(user):
                    session['loggedin'] = True
                    session['id'] = user.id
                    session['username'] = user.username                    
                    return redirect(url_for('pages.dashboard'))
    return render_template('pages/login.html', form=form)


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('pages.login'))


@bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('pages.login'))
    return render_template('pages/register.html', form=form)


@bp.route('/profile')
@login_required
def profile():
    # Check if the user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        user = User.query.filter_by(username=session['username']).first()
        # Show the profile page with account info
        return render_template('pages/profile.html', user=user)
    # User is not logged in redirect to login page
    return redirect(url_for('pages.login'))


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        input_path=app.config['UPLOAD_FOLDER']
        f.save(os.path.join(input_path, filename))
        ft = filetype_validation(input_path, filename)
        return redirect(url_for('pages.success', input_path=input_path, file_type=ft, file_name=filename))
    return render_template('pages/upload.html',form=form)


@bp.route('/success')
# @bp.route('/success/<input_path>/<file_type>/<file_name>')
@login_required
# def success(input_path, file_type, file_name):
def success():
    input_path = request.args.get('input_path')
    file_type = request.args.get('file_type') 
    file_name = request.args.get('file_name')
    # ... rest of your function logic
    describe_params={"file_name":file_name, "input_path":input_path}

    try:
        match file_type:
            case 'live-optics':
                vm_data_df = pd.DataFrame(lova_conversion(**describe_params))
            case 'rv-tools':
                vm_data_df = pd.DataFrame(rvtools_conversion(**describe_params))
            case 'invalid':
                return render_template('pages/error.html', fn=file_name, ft=file_type)

        try:
            os.remove(os.path.join(input_path, file_name))
            print('File deleted...', file=sys.stderr)  # Print to stderr
        except:
            print('File deletion failed...', file=sys.stderr)  # Print to stderr

        if vm_data_df is not None:
            # access the result in the template, for example {{ vms }}
            vmdf_html = vm_data_df.to_html(classes=["table", "table-sm","table-striped", "text-center","table-responsive","table-hover", "table-dark"])
            return render_template('pages/success.html', fn=file_name, ft=file_type, tables=[vmdf_html], titles=[''])
        else:
            print()
            print("Something went wrong.  Please check your syntax and try again.")

    except FileNotFoundError:
        print("The file was not found.")
        return redirect(url_for('pages.upload'))


@bp.route("/about")
def about():
    return render_template("pages/about.html")

