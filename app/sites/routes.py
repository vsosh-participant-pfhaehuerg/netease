from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash, send_from_directory
import os
import shutil
from werkzeug.utils import secure_filename

sites = Blueprint('sites', __name__)

@sites.route('/static', methods=['GET', 'POST'])
def static_site():
    # Get list of static sites
    sites = []
    try:
        base_dir = current_app.config['WEBSITE_ROOT']
        if os.path.isdir(base_dir):
            sites = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
            sites.sort()
    except Exception as e:
        flash(f'Error reading sites directory: {str(e)}', 'danger')
    
    return render_template('sites/static_site.html', sites=sites)

@sites.route('/file_manager/')
@sites.route('/file_manager/<path:site_path>')
def file_manager(site_path=''):
    # Normalize the path and prevent directory traversal
    if site_path and (site_path.startswith('/') or '..' in site_path):
        flash('Invalid path specified', 'danger')
        return redirect(url_for('sites.file_manager'))
    
    # Base directory for file operations
    base_dir = current_app.config['WEBSITE_ROOT']
    current_dir = os.path.join(base_dir, site_path).rstrip('/')
    
    # Ensure the path exists and is a directory
    if not os.path.isdir(current_dir):
        flash(f'Directory does not exist: {site_path}', 'danger')
        return redirect(url_for('sites.file_manager'))
    
    # Get parent directory
    parent_dir = os.path.dirname(site_path) if site_path else None
    
    # Get directories and files
    try:
        items = os.listdir(current_dir)
        directories = [item for item in items if os.path.isdir(os.path.join(current_dir, item))]
        files = [item for item in items if os.path.isfile(os.path.join(current_dir, item))]
        
        # Sort directories and files alphabetically
        directories.sort()
        files.sort()
    except Exception as e:
        flash(f'Error reading directory: {str(e)}', 'danger')
        return redirect(url_for('sites.file_manager'))
    
    # Create breadcrumbs
    breadcrumbs = []
    if site_path:
        parts = site_path.split('/')
        for i in range(len(parts)):
            breadcrumbs.append({
                'name': parts[i],
                'path': '/'.join(parts[:i+1])
            })
    
    return render_template('sites/file_manager.html', 
                          current_path=site_path,
                          parent_dir=parent_dir,
                          directories=directories,
                          files=files,
                          breadcrumbs=breadcrumbs)

@sites.route('/upload_file/<path:site_path>', methods=['POST'])
def upload_file(site_path=''):
    # Normalize the path and prevent directory traversal
    if site_path and (site_path.startswith('/') or '..' in site_path):
        flash('Invalid path specified', 'danger')
        return redirect(url_for('sites.file_manager'))
    
    # Base directory for file operations
    base_dir = current_app.config['WEBSITE_ROOT']
    upload_dir = os.path.join(base_dir, site_path)
    
    # Ensure the directory exists
    if not os.path.isdir(upload_dir):
        flash(f'Directory does not exist: {site_path}', 'danger')
        return redirect(url_for('sites.file_manager'))
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('sites.file_manager', site_path=site_path))
    
    files = request.files.getlist('file')
    
    # If no file was selected
    if len(files) == 0 or files[0].filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('sites.file_manager', site_path=site_path))
    
    # Save each file
    for file in files:
        filename = secure_filename(file.filename)
        if filename:
            try:
                file.save(os.path.join(upload_dir, filename))
                flash(f'Uploaded {filename} successfully', 'success')
            except Exception as e:
                flash(f'Error uploading {filename}: {str(e)}', 'danger')
    
    return redirect(url_for('sites.file_manager', site_path=site_path))

@sites.route('/create_directory/<path:site_path>', methods=['POST'])
def create_directory(site_path=''):
    # Normalize the path and prevent directory traversal
    if site_path and (site_path.startswith('/') or '..' in site_path):
        flash('Invalid path specified', 'danger')
        return redirect(url_for('sites.file_manager'))
    
    # Get the directory name from the form
    dirname = request.form.get('dirname', '').strip()
    if not dirname:
        flash('No directory name provided', 'danger')
        return redirect(url_for('sites.file_manager', site_path=site_path))
    
    # Validate directory name
    if '/' in dirname or '\\' in dirname or '..' in dirname:
        flash('Invalid directory name', 'danger')
        return redirect(url_for('sites.file_manager', site_path=site_path))
    
    # Base directory for file operations
    base_dir = current_app.config['WEBSITE_ROOT']
    new_dir_path = os.path.join(base_dir, site_path, dirname)
    
    # Create the directory
    try:
        os.makedirs(new_dir_path, exist_ok=True)
        flash(f'Created directory: {dirname}', 'success')
    except Exception as e:
        flash(f'Error creating directory: {str(e)}', 'danger')
    
    return redirect(url_for('sites.file_manager', site_path=site_path))

@sites.route('/delete_item/<path:site_path>', methods=['POST'])
def delete_item(site_path=''):
    # Normalize the path and prevent directory traversal
    if site_path and (site_path.startswith('/') or '..' in site_path):
        flash('Invalid path specified', 'danger')
        return redirect(url_for('sites.file_manager'))
    
    # Get item details from form
    item_name = request.form.get('item_name', '').strip()
    item_type = request.form.get('item_type', '').strip()
    
    if not item_name or not item_type:
        flash('Missing item details', 'danger')
        return redirect(url_for('sites.file_manager', site_path=site_path))
    
    # Validate item name
    if '/' in item_name or '\\' in item_name or '..' in item_name:
        flash('Invalid item name', 'danger')
        return redirect(url_for('sites.file_manager', site_path=site_path))
    
    # Base directory for file operations
    base_dir = current_app.config['WEBSITE_ROOT']
    item_path = os.path.join(base_dir, site_path, item_name)
    
    try:
        if item_type == 'file':
            if os.path.isfile(item_path):
                os.remove(item_path)
                flash(f'Deleted file: {item_name}', 'success')
            else:
                flash(f'File not found: {item_name}', 'danger')
        elif item_type == 'directory':
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                flash(f'Deleted directory: {item_name}', 'success')
            else:
                flash(f'Directory not found: {item_name}', 'danger')
        else:
            flash(f'Invalid item type: {item_type}', 'danger')
    except Exception as e:
        flash(f'Error deleting {item_type}: {str(e)}', 'danger')
    
    return redirect(url_for('sites.file_manager', site_path=site_path))

@sites.route('/download_file/<path:site_path>')
def download_file(site_path=''):
    # Normalize the path and prevent directory traversal
    if not site_path or site_path.startswith('/') or '..' in site_path:
        flash('Invalid path specified', 'danger')
        return redirect(url_for('sites.file_manager'))
    
    # Base directory for file operations
    base_dir = current_app.config['WEBSITE_ROOT']
    file_path = os.path.join(base_dir, site_path)
    
    # Ensure the file exists and is a file
    if not os.path.isfile(file_path):
        flash(f'File not found: {site_path}', 'danger')
        return redirect(url_for('sites.file_manager'))
    
    # Get directory path for redirecting back after download
    dir_path = os.path.dirname(site_path)
    
    # Return the file for download
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'danger')
        return redirect(url_for('sites.file_manager', site_path=dir_path)) 