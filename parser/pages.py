from flask import Blueprint, redirect, render_template, url_for
from app import db, bcrypt
from transform.data_validation import filetype_validation
from transform.transform_lova import lova_conversion
from transform.transform_rvtools import rvtools_conversion
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user
from forms import RegisterForm, LoginForm, UploadFileForm, CreateProjectForm, CreateWorkloadForm
from models import User, Workload, Project
from flask import current_app as app


bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    return render_template("pages/home.html")

@bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("pages/dashboard.html")

@bp.route("/create_project", methods=['GET', 'POST'])
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
                    return redirect(url_for('pages.dashboard'))
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(fieldName, err)
    return render_template('pages/login.html', form=form)

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
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

    # if request.method == 'POST':
    #     # check if the post request has the file part
    #     if 'file' not in request.files:
    #         flash('No file part')
    #         return redirect(request.url)
    #     file = request.files['file']

    #     # If the user does not select a file, the browser submits an empty file without a filename.
    #     if file.filename == '':
    #         flash('No selected file')
    #         return redirect(request.url)
    #     if file and allowed_file(file.filename):
    #         input_path=app.config['UPLOAD_FOLDER']
    #         filename = secure_filename(file.filename)
    #         file.save(os.path.join(input_path, filename))

    #         ft = filetype_validation(input_path, filename)
    #         return redirect(url_for('pages.success', input_path=input_path, file_type=ft, file_name=filename))
    # return render_template('pages/upload.html')

@bp.route('/success/<input_path>/<file_type>/<file_name>')
@login_required
def success(input_path, file_type, file_name):
    describe_params={"file_name":file_name, "input_path":input_path}

    match file_type:
        case 'live-optics':
            vm_data_df = pd.DataFrame(lova_conversion(**describe_params))
        case 'rv-tools':
            vm_data_df = pd.DataFrame(rvtools_conversion(**describe_params))
        case 'invalid':
            return render_template('pages/error.html', fn=file_name, ft=file_type)

    if vm_data_df is not None:
        # access the result in the tempalte, for example {{ vms }}
        vmdf_html = vm_data_df.to_html(classes=["table", "table-sm","table-striped", "text-center","table-responsive","table-hover", "table-dark"])
        return render_template('pages/success.html', fn=file_name, ft=file_type, tables=[vmdf_html], titles=[''])
    else:
        print()
        print("Something went wrong.  Please check your syntax and try again.")


@bp.route("/about")
def about():
    return render_template("pages/about.html")

