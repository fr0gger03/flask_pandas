from flask import Blueprint, request, redirect, render_template, url_for, session, flash, abort, make_response
from flask import current_app as app
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from parser.app import db, bcrypt
from parser.forms import RegisterForm, LoginForm, UploadFileForm, CreateProjectForm, CreateWorkloadForm, EditProjectForm, EditWorkloadForm
from parser.models import User, Workload, Project
from sqlalchemy import func, desc

import os, sys
import pandas as pd
import json
from parser.transform.data_validation import filetype_validation
from parser.transform.transform_lova import lova_conversion
from parser.transform.transform_rvtools import rvtools_conversion


bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    context = {}
    if current_user.is_authenticated:
        # Get basic statistics for authenticated users
        user_projects = Project.query.filter_by(userid=current_user.id).all()
        total_workloads = sum(len(project.workloads) for project in user_projects)
        
        # Get recent projects (last 3)
        recent_projects = Project.query.filter_by(userid=current_user.id)\
                                     .order_by(desc(Project.pid))\
                                     .limit(3).all()
        
        context.update({
            'user_projects_count': len(user_projects),
            'total_workloads': total_workloads,
            'recent_projects': recent_projects
        })
    
    return render_template("pages/home.html", **context)


@bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    # Get all projects for the current user
    user_projects = Project.query.filter_by(userid=current_user.id).all()
    
    # Calculate total workloads across all projects
    total_workloads = sum(len(project.workloads) for project in user_projects)
    
    return render_template("pages/dashboard.html", 
                         user_projects=user_projects, 
                         total_workloads=total_workloads)


@bp.route("/create_project", methods=['GET', 'POST'])
@login_required
def create_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        new_project = Project(
            projectname=form.projectname.data,
            userid=current_user.id
        )
        try:
            db.session.add(new_project)
            db.session.commit()
            flash(f'Project "{form.projectname.data}" created successfully!', 'success')
            return redirect(url_for('pages.view_project', project_id=new_project.pid))
        except Exception as e:
            db.session.rollback()
            flash('Error creating project. Please try again.', 'error')
            app.logger.error(f'Error creating project: {e}')
    return render_template("pages/create_project.html", form=form)


@bp.route("/view_project/<int:project_id>")
@login_required
def view_project(project_id):
    project = Project.query.filter_by(pid=project_id, userid=current_user.id).first_or_404()
    
    # Calculate summary statistics
    total_vcpus = sum(workload.vcpu or 0 for workload in project.workloads)
    total_vram = sum(float(workload.vram or 0) / 1024 for workload in project.workloads)  # Convert MB to GB
    total_storage = sum(workload.total_storage_gb for workload in project.workloads)
    
    return render_template("pages/view_project.html", 
                         project=project,
                         total_vcpus=total_vcpus,
                         total_vram=total_vram,
                         total_storage=total_storage)


@bp.route("/edit_project/<int:project_id>", methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.filter_by(pid=project_id, userid=current_user.id).first_or_404()
    form = EditProjectForm(original_projectname=project.projectname)
    
    if form.validate_on_submit():
        project.projectname = form.projectname.data
        try:
            db.session.commit()
            flash(f'Project updated successfully!', 'success')
            return redirect(url_for('pages.view_project', project_id=project.pid))
        except Exception as e:
            db.session.rollback()
            flash('Error updating project. Please try again.', 'error')
            app.logger.error(f'Error updating project: {e}')
    elif request.method == 'GET':
        form.projectname.data = project.projectname
    
    return render_template("pages/edit_project.html", form=form, project=project)


@bp.route("/delete_project/<int:project_id>", methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.filter_by(pid=project_id, userid=current_user.id).first_or_404()
    project_name = project.projectname
    
    try:
        db.session.delete(project)
        db.session.commit()
        flash(f'Project "{project_name}" and all its workloads have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting project. Please try again.', 'error')
        app.logger.error(f'Error deleting project: {e}')
    
    return redirect(url_for('pages.dashboard'))


@bp.route("/create_workload/<int:project_id>", methods=['GET', 'POST'])
@login_required
def create_workload(project_id):
    project = Project.query.filter_by(pid=project_id, userid=current_user.id).first_or_404()
    form = CreateWorkloadForm()
    
    if form.validate_on_submit():
        new_workload = Workload(
            pid=project.pid,
            vmname=form.vmname.data,
            mobid=form.mobid.data or None,
            os=form.os.data or None,
            os_name=form.os_name.data or None,
            vmstate=form.vmstate.data,
            vcpu=form.vcpu.data,
            vram=form.vram.data,
            cluster=form.cluster.data or None,
            virtualdatacenter=form.virtualdatacenter.data or None,
            ip_addresses=form.ip_addresses.data or None,
            vinfo_provisioned=form.vinfo_provisioned.data,
            vinfo_used=form.vinfo_used.data,
            vmdktotal=form.vmdktotal.data,
            vmdkused=form.vmdkused.data,
            readiops=form.readiops.data,
            writeiops=form.writeiops.data,
            peakreadiops=form.peakreadiops.data,
            peakwriteiops=form.peakwriteiops.data,
            readthroughput=form.readthroughput.data,
            writethroughput=form.writethroughput.data,
            peakreadthroughput=form.peakreadthroughput.data,
            peakwritethroughput=form.peakwritethroughput.data
        )
        
        try:
            db.session.add(new_workload)
            db.session.commit()
            flash(f'Workload "{form.vmname.data}" added successfully!', 'success')
            return redirect(url_for('pages.view_project', project_id=project.pid))
        except Exception as e:
            db.session.rollback()
            flash('Error creating workload. Please try again.', 'error')
            app.logger.error(f'Error creating workload: {e}')
    
    return render_template("pages/create_workload.html", form=form, project=project)


@bp.route("/view_workload/<int:workload_id>")
@login_required
def view_workload(workload_id):
    workload = Workload.query.join(Project).filter(
        Workload.vmid == workload_id,
        Project.userid == current_user.id
    ).first_or_404()
    
    return render_template("pages/view_workload.html", workload=workload)


@bp.route("/edit_workload/<int:workload_id>", methods=['GET', 'POST'])
@login_required
def edit_workload(workload_id):
    workload = Workload.query.join(Project).filter(
        Workload.vmid == workload_id,
        Project.userid == current_user.id
    ).first_or_404()
    
    form = EditWorkloadForm()
    
    if form.validate_on_submit():
        # Update all fields
        workload.vmname = form.vmname.data
        workload.mobid = form.mobid.data or None
        workload.os = form.os.data or None
        workload.os_name = form.os_name.data or None
        workload.vmstate = form.vmstate.data
        workload.vcpu = form.vcpu.data
        workload.vram = form.vram.data
        workload.cluster = form.cluster.data or None
        workload.virtualdatacenter = form.virtualdatacenter.data or None
        workload.ip_addresses = form.ip_addresses.data or None
        workload.vinfo_provisioned = form.vinfo_provisioned.data
        workload.vinfo_used = form.vinfo_used.data
        workload.vmdktotal = form.vmdktotal.data
        workload.vmdkused = form.vmdkused.data
        workload.readiops = form.readiops.data
        workload.writeiops = form.writeiops.data
        workload.peakreadiops = form.peakreadiops.data
        workload.peakwriteiops = form.peakwriteiops.data
        workload.readthroughput = form.readthroughput.data
        workload.writethroughput = form.writethroughput.data
        workload.peakreadthroughput = form.peakreadthroughput.data
        workload.peakwritethroughput = form.peakwritethroughput.data
        
        try:
            db.session.commit()
            flash(f'Workload "{form.vmname.data}" updated successfully!', 'success')
            return redirect(url_for('pages.view_project', project_id=workload.pid))
        except Exception as e:
            db.session.rollback()
            flash('Error updating workload. Please try again.', 'error')
            app.logger.error(f'Error updating workload: {e}')
    elif request.method == 'GET':
        # Populate form with current values
        form.vmname.data = workload.vmname
        form.mobid.data = workload.mobid
        form.os.data = workload.os
        form.os_name.data = workload.os_name
        form.vmstate.data = workload.vmstate
        form.vcpu.data = workload.vcpu
        form.vram.data = workload.vram
        form.cluster.data = workload.cluster
        form.virtualdatacenter.data = workload.virtualdatacenter
        form.ip_addresses.data = workload.ip_addresses
        form.vinfo_provisioned.data = workload.vinfo_provisioned
        form.vinfo_used.data = workload.vinfo_used
        form.vmdktotal.data = workload.vmdktotal
        form.vmdkused.data = workload.vmdkused
        form.readiops.data = workload.readiops
        form.writeiops.data = workload.writeiops
        form.peakreadiops.data = workload.peakreadiops
        form.peakwriteiops.data = workload.peakwriteiops
        form.readthroughput.data = workload.readthroughput
        form.writethroughput.data = workload.writethroughput
        form.peakreadthroughput.data = workload.peakreadthroughput
        form.peakwritethroughput.data = workload.peakwritethroughput
    
    return render_template("pages/edit_workload.html", form=form, workload=workload)


@bp.route("/delete_workload/<int:workload_id>", methods=['POST'])
@login_required
def delete_workload(workload_id):
    workload = Workload.query.join(Project).filter(
        Workload.vmid == workload_id,
        Project.userid == current_user.id
    ).first_or_404()
    
    workload_name = workload.vmname
    project_id = workload.pid
    
    try:
        db.session.delete(workload)
        db.session.commit()
        flash(f'Workload "{workload_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting workload. Please try again.', 'error')
        app.logger.error(f'Error deleting workload: {e}')
    
    return redirect(url_for('pages.view_project', project_id=project_id))


@bp.route("/export_project/<int:project_id>")
@login_required
def export_project(project_id):
    project = Project.query.filter_by(pid=project_id, userid=current_user.id).first_or_404()
    
    if not project.workloads:
        flash('No workloads to export in this project.', 'warning')
        return redirect(url_for('pages.view_project', project_id=project_id))
    
    # Create DataFrame from workloads
    workload_data = []
    for workload in project.workloads:
        workload_data.append({
            'VM Name': workload.vmname,
            'MOB ID': workload.mobid,
            'Operating System': workload.os,
            'Hostname': workload.os_name,
            'VM State': workload.vmstate,
            'vCPU': workload.vcpu,
            'vRAM (MB)': workload.vram,
            'Cluster': workload.cluster,
            'Datacenter': workload.virtualdatacenter,
            'IP Addresses': workload.ip_addresses,
            'vInfo Provisioned (GB)': float(workload.vinfo_provisioned or 0),
            'vInfo Used (GB)': float(workload.vinfo_used or 0),
            'Total Storage (GB)': float(workload.vmdktotal or 0),
            'Used Storage (GB)': float(workload.vmdkused or 0),
            'Read IOPS': float(workload.readiops or 0),
            'Write IOPS': float(workload.writeiops or 0),
            'Peak Read IOPS': float(workload.peakreadiops or 0),
            'Peak Write IOPS': float(workload.peakwriteiops or 0),
            'Read Throughput (MB/s)': float(workload.readthroughput or 0),
            'Write Throughput (MB/s)': float(workload.writethroughput or 0),
            'Peak Read Throughput (MB/s)': float(workload.peakreadthroughput or 0),
            'Peak Write Throughput (MB/s)': float(workload.peakwritethroughput or 0)
        })
    
    df = pd.DataFrame(workload_data)
    
    # Create CSV response
    output = df.to_csv(index=False)
    response = make_response(output)
    response.headers["Content-Disposition"] = f"attachment; filename={project.projectname}_workloads.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response


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
@bp.route('/upload/<int:project_id>', methods=['GET', 'POST'])
@login_required
def upload(project_id=None):
    # Get user's projects for selection
    user_projects = Project.query.filter_by(userid=current_user.id).all()
    
    if not user_projects:
        flash('You need to create a project first before uploading workload data.', 'warning')
        return redirect(url_for('pages.create_project'))
    
    # If project_id provided, validate it belongs to user
    selected_project = None
    if project_id:
        selected_project = Project.query.filter_by(pid=project_id, userid=current_user.id).first_or_404()
    
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        input_path = app.config['UPLOAD_FOLDER']
        f.save(os.path.join(input_path, filename))
        ft = filetype_validation(input_path, filename)
        
        # Pass project_id to success page
        target_project_id = project_id or request.form.get('project_id')
        return redirect(url_for('pages.process_upload', 
                              input_path=input_path, 
                              file_type=ft, 
                              file_name=filename,
                              project_id=target_project_id))
    
    return render_template('pages/upload.html', 
                         form=form, 
                         user_projects=user_projects,
                         selected_project=selected_project)


@bp.route('/process_upload')
@login_required
def process_upload():
    input_path = request.args.get('input_path')
    file_type = request.args.get('file_type') 
    file_name = request.args.get('file_name')
    project_id = request.args.get('project_id')
    
    if not all([input_path, file_type, file_name, project_id]):
        flash('Missing upload parameters. Please try uploading again.', 'error')
        return redirect(url_for('pages.upload'))
    
    # Validate project belongs to user
    project = Project.query.filter_by(pid=project_id, userid=current_user.id).first_or_404()
    
    describe_params = {"file_name": file_name, "input_path": input_path}
    
    try:
        vm_data_df = None
        match file_type:
            case 'live-optics':
                vm_data_df = pd.DataFrame(lova_conversion(**describe_params))
            case 'rv-tools':
                vm_data_df = pd.DataFrame(rvtools_conversion(**describe_params))
            case 'invalid':
                try:
                    os.remove(os.path.join(input_path, file_name))
                except:
                    pass
                flash(f'Invalid file type for {file_name}. Please upload a valid LiveOptics or RVTools file.', 'error')
                return redirect(url_for('pages.upload'))
        
        # Clean up uploaded file
        try:
            os.remove(os.path.join(input_path, file_name))
            app.logger.info(f'File {file_name} deleted after processing')
        except Exception as e:
            app.logger.warning(f'File deletion failed for {file_name}: {e}')
        
        if vm_data_df is not None and not vm_data_df.empty:
            # Store processed data in session for preview
            session['processed_data'] = vm_data_df.to_json(orient='records')
            session['project_id'] = project_id
            session['file_name'] = file_name
            session['file_type'] = file_type
            
            # Generate HTML table for preview
            vmdf_html = vm_data_df.to_html(
                classes=["table", "table-sm", "table-striped", "text-center", 
                         "table-responsive", "table-hover", "table-dark"],
                table_id="workload-preview-table"
            )
            
            return render_template('pages/upload_preview.html', 
                                 project=project,
                                 file_name=file_name, 
                                 file_type=file_type, 
                                 tables=[vmdf_html], 
                                 workload_count=len(vm_data_df))
        else:
            flash('No valid workload data found in the uploaded file.', 'error')
            return redirect(url_for('pages.upload'))
    
    except Exception as e:
        app.logger.error(f'Error processing upload: {e}')
        # Clean up file on error
        try:
            os.remove(os.path.join(input_path, file_name))
        except:
            pass
        flash('Error processing uploaded file. Please check the file format and try again.', 'error')
        return redirect(url_for('pages.upload'))


@bp.route('/save_workloads', methods=['POST'])
@login_required
def save_workloads():
    # Get processed data from session
    processed_data_json = session.get('processed_data')
    project_id = session.get('project_id')
    file_name = session.get('file_name')
    
    if not all([processed_data_json, project_id]):
        flash('No processed data found. Please upload a file first.', 'error')
        return redirect(url_for('pages.upload'))
    
    # Validate project belongs to user
    project = Project.query.filter_by(pid=project_id, userid=current_user.id).first_or_404()
    
    try:
        # Convert JSON back to DataFrame
        processed_data = json.loads(processed_data_json)
        vm_data_df = pd.DataFrame(processed_data)
        
        workloads_created = 0
        workloads_failed = 0
        
        # Create workload objects from DataFrame
        for _, row in vm_data_df.iterrows():
            try:
                workload = Workload(
                    pid=project.pid,
                    vmname=row.get('vmName'),
                    mobid=row.get('vmId'),  # MOB ID maps to vmId in processed data
                    os=row.get('os'),
                    os_name=row.get('os_name'),
                    vmstate=row.get('vmState'),
                    vcpu=int(row.get('vCpu', 0)) if pd.notna(row.get('vCpu')) else 0,
                    vram=int(row.get('vRam', 0) * 1024) if pd.notna(row.get('vRam')) else 0,  # Convert GB to MB
                    cluster=row.get('cluster'),
                    virtualdatacenter=row.get('virtualDatacenter'),
                    ip_addresses=row.get('ip_addresses'),
                    vinfo_provisioned=row.get('vinfo_provisioned'),
                    vinfo_used=row.get('vinfo_used'),
                    vmdktotal=row.get('vmdkTotal'),
                    vmdkused=row.get('vmdkUsed'),
                    readiops=row.get('readIOPS'),
                    writeiops=row.get('writeIOPS'),
                    peakreadiops=row.get('peakReadIOPS'),
                    peakwriteiops=row.get('peakWriteIOPS'),
                    readthroughput=row.get('readThroughput'),
                    writethroughput=row.get('writeThroughput'),
                    peakreadthroughput=row.get('peakReadThroughput'),
                    peakwritethroughput=row.get('peakWriteThroughput')
                )
                db.session.add(workload)
                workloads_created += 1
            except Exception as e:
                workloads_failed += 1
                app.logger.error(f'Error creating workload from row: {e}')
                continue
        
        # Commit all workloads
        db.session.commit()
        
        # Clear session data
        session.pop('processed_data', None)
        session.pop('project_id', None)
        session.pop('file_name', None)
        session.pop('file_type', None)
        
        # Provide user feedback
        if workloads_created > 0:
            flash(f'Successfully imported {workloads_created} workloads to project "{project.projectname}".', 'success')
            if workloads_failed > 0:
                flash(f'{workloads_failed} workloads could not be imported due to data issues.', 'warning')
        else:
            flash('No workloads could be imported. Please check your file format.', 'error')
        
        return redirect(url_for('pages.view_project', project_id=project.pid))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error saving workloads: {e}')
        flash('Error saving workloads to database. Please try again.', 'error')
        return redirect(url_for('pages.upload'))


@bp.route('/cancel_upload', methods=['POST'])
@login_required
def cancel_upload():
    # Clear session data
    session.pop('processed_data', None)
    session.pop('project_id', None)
    session.pop('file_name', None)
    session.pop('file_type', None)
    
    flash('Upload cancelled.', 'info')
    return redirect(url_for('pages.dashboard'))


@bp.route("/analytics")
@login_required
def analytics():
    # Total projects and workloads (using unique vmid)
    project_count = Project.query.filter_by(userid=current_user.id).count()
    total_workloads = Workload.query.join(Project).filter(Project.userid==current_user.id).count()

    # Group workloads by attributes (using distinct vmid for accurate counting)
    os_distribution = db.session.query(
        Workload.os, 
        func.count(func.distinct(Workload.vmid))
    ).join(Project).filter(
        Project.userid==current_user.id,
        Workload.os.isnot(None),
        Workload.os != ''
    ).group_by(Workload.os).order_by(desc(func.count(func.distinct(Workload.vmid)))).all()
    
    cpu_distribution = db.session.query(
        Workload.vcpu, 
        func.count(func.distinct(Workload.vmid))
    ).join(Project).filter(
        Project.userid==current_user.id,
        Workload.vcpu.isnot(None)
    ).group_by(Workload.vcpu).order_by(desc(func.count(func.distinct(Workload.vmid)))).all()
    
    cluster_distribution = db.session.query(
        Workload.cluster, 
        func.count(func.distinct(Workload.vmid))
    ).join(Project).filter(
        Project.userid==current_user.id,
        Workload.cluster.isnot(None),
        Workload.cluster != ''
    ).group_by(Workload.cluster).order_by(desc(func.count(func.distinct(Workload.vmid)))).all()
    
    # VM State distribution
    state_distribution = db.session.query(
        Workload.vmstate, 
        func.count(func.distinct(Workload.vmid))
    ).join(Project).filter(
        Project.userid==current_user.id,
        Workload.vmstate.isnot(None),
        Workload.vmstate != ''
    ).group_by(Workload.vmstate).order_by(desc(func.count(func.distinct(Workload.vmid)))).all()
    
    # Resource totals (using distinct vmid to avoid double counting)
    resource_totals = db.session.query(
        func.sum(Workload.vcpu),
        func.sum(Workload.vram),
        func.sum(Workload.vmdktotal)
    ).join(Project).filter(
        Project.userid==current_user.id
    ).first()
    
    total_vcpus = int(resource_totals[0] or 0)
    total_vram_mb = int(resource_totals[1] or 0)
    total_vram_gb = round(total_vram_mb / 1024, 2) if total_vram_mb else 0
    total_storage_gb = round(float(resource_totals[2] or 0), 2)
    
    # Average resource utilization
    avg_cpu_per_vm = round(total_vcpus / total_workloads, 2) if total_workloads > 0 else 0
    avg_ram_per_vm = round(total_vram_gb / total_workloads, 2) if total_workloads > 0 else 0
    avg_storage_per_vm = round(total_storage_gb / total_workloads, 2) if total_workloads > 0 else 0

    return render_template("pages/analytics.html", 
                           project_count=project_count, 
                           total_workloads=total_workloads, 
                           os_distribution=os_distribution,
                           cpu_distribution=cpu_distribution,
                           cluster_distribution=cluster_distribution,
                           state_distribution=state_distribution,
                           total_vcpus=total_vcpus,
                           total_vram_gb=total_vram_gb,
                           total_storage_gb=total_storage_gb,
                           avg_cpu_per_vm=avg_cpu_per_vm,
                           avg_ram_per_vm=avg_ram_per_vm,
                           avg_storage_per_vm=avg_storage_per_vm)


@bp.route("/reports")
@login_required
def reports():
    # Implement any additional logic for generating reports
    return render_template("pages/reports.html")


@bp.route("/about")
def about():
    return render_template("pages/about.html")

