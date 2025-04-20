from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash, send_from_directory
import validators
import os
import shutil
from werkzeug.utils import secure_filename

sites_bp = Blueprint('sites', __name__)

@sites_bp.route('/')
def index():
    return render_template('sites/index.html')

@sites_bp.route('/proxy')
def proxy():
    return render_template('sites/proxy.html')

@sites_bp.route('/static')
def static_site():
    # Get directories in /var/www to display in dropdown
    www_dirs = []
    try:
        if os.path.exists('/var/www'):
            www_dirs = [d for d in os.listdir('/var/www') if os.path.isdir(os.path.join('/var/www', d))]
    except:
        pass  # Handle permission issues gracefully
    
    return render_template('sites/static.html', www_dirs=www_dirs)

@sites_bp.route('/advanced')
def advanced():
    return render_template('sites/advanced.html')

@sites_bp.route('/create_proxy', methods=['POST'])
def create_proxy():
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    
    server_name = request.form.get('server_name')
    proxy_pass = request.form.get('proxy_pass')
    listen_port = request.form.get('listen_port', 80)
    config_name = request.form.get('config_name')
    
    # Validation
    errors = []
    
    if not server_name:
        errors.append('Server name is required')
    elif not validators.domain(server_name) and server_name != "localhost":
        errors.append('Invalid server name')
    
    if not proxy_pass:
        errors.append('Proxy pass URL is required')
    
    try:
        listen_port = int(listen_port)
        if listen_port < 1 or listen_port > 65535:
            errors.append('Port must be between 1 and 65535')
    except:
        errors.append('Port must be a number')
    
    if not config_name:
        errors.append('Configuration name is required')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('sites.proxy'))
    
    # Add .conf extension if not present
    if not config_name.endswith('.conf'):
        config_name += '.conf'
    
    # Generate configuration
    config_content = nginx_manager.create_proxy_config(
        server_name=server_name,
        proxy_pass=proxy_pass,
        listen_port=listen_port,
        ssl=False
    )
    
    # Save configuration
    success = nginx_manager.save_config(config_name, config_content)
    
    if success:
        flash(f'Proxy configuration {config_name} created successfully', 'success')
        
        # Test the configuration before enabling
        test_success, test_output = nginx_manager.test_config()
        
        if test_success:
            # Enable the configuration
            enable_success = nginx_manager.enable_config(config_name)
            
            if enable_success:
                flash(f'Configuration {config_name} enabled successfully', 'success')
                
                # Reload Nginx to apply changes
                reload_success, reload_output = nginx_manager.reload_nginx()
                
                if reload_success:
                    flash('Nginx reloaded successfully', 'success')
                else:
                    flash(f'Failed to reload Nginx: {reload_output}', 'error')
            else:
                flash(f'Failed to enable configuration {config_name}', 'error')
        else:
            flash(f'Configuration has errors, not enabled: {test_output}', 'error')
        
        return redirect(url_for('configs.view', config_name=config_name))
    else:
        flash('Failed to create configuration', 'error')
        return redirect(url_for('sites.proxy'))

@sites_bp.route('/create_static', methods=['POST'])
def create_static():
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    
    server_name = request.form.get('server_name')
    root_path = request.form.get('root_path')
    site_name = request.form.get('site_name', '')
    create_dir = request.form.get('create_dir') == 'on'
    listen_port = request.form.get('listen_port', 80)
    index = request.form.get('index', 'index.html')
    config_name = request.form.get('config_name')
    
    # Validation
    errors = []
    
    if not server_name:
        errors.append('Server name is required')
    elif not validators.domain(server_name) and server_name != "localhost":
        errors.append('Invalid server name')
    
    # Handle root path creation if needed
    if create_dir and site_name:
        # Create directory in /var/www
        root_path = f'/var/www/{secure_filename(site_name)}'
        try:
            if not os.path.exists(root_path):
                os.makedirs(root_path, exist_ok=True)
                flash(f'Directory {root_path} created successfully', 'success')
        except Exception as e:
            errors.append(f'Failed to create directory: {str(e)}')
    elif not root_path:
        errors.append('Root path is required')
    
    try:
        listen_port = int(listen_port)
        if listen_port < 1 or listen_port > 65535:
            errors.append('Port must be between 1 and 65535')
    except:
        errors.append('Port must be a number')
    
    if not config_name:
        errors.append('Configuration name is required')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('sites.static_site'))
    
    # Add .conf extension if not present
    if not config_name.endswith('.conf'):
        config_name += '.conf'
    
    # Generate configuration
    config_content = nginx_manager.create_static_config(
        server_name=server_name,
        root_path=root_path,
        listen_port=listen_port,
        index=index
    )
    
    # Save configuration
    success = nginx_manager.save_config(config_name, config_content)
    
    if success:
        flash(f'Static site configuration {config_name} created successfully', 'success')
        
        # Test the configuration before enabling
        test_success, test_output = nginx_manager.test_config()
        
        if test_success:
            # Enable the configuration
            enable_success = nginx_manager.enable_config(config_name)
            
            if enable_success:
                flash(f'Configuration {config_name} enabled successfully', 'success')
                
                # Reload Nginx to apply changes
                reload_success, reload_output = nginx_manager.reload_nginx()
                
                if reload_success:
                    flash('Nginx reloaded successfully', 'success')
                else:
                    flash(f'Failed to reload Nginx: {reload_output}', 'error')
            else:
                flash(f'Failed to enable configuration {config_name}', 'error')
        else:
            flash(f'Configuration has errors, not enabled: {test_output}', 'error')
        
        # Redirect to the file manager for the static site
        if root_path and root_path.startswith('/var/www/'):
            site_path = root_path[9:]  # Remove the '/var/www/' prefix
            return redirect(url_for('sites.file_manager', site_path=site_path))
        else:
            return redirect(url_for('configs.view', config_name=config_name))
    else:
        flash('Failed to create configuration', 'error')
        return redirect(url_for('sites.static_site'))

@sites_bp.route('/file_manager/<path:site_path>')
def file_manager(site_path):
    full_path = os.path.join('/var/www', site_path)
    
    # Security check to prevent directory traversal
    if not full_path.startswith('/var/www'):
        flash('Invalid path specified', 'error')
        return redirect(url_for('sites.static_site'))
    
    # Get list of files and directories
    try:
        if not os.path.exists(full_path):
            flash('Directory does not exist', 'error')
            return redirect(url_for('sites.static_site'))
        
        files = []
        dirs = []
        
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                dirs.append({
                    'name': item,
                    'path': os.path.join(site_path, item),
                    'type': 'directory'
                })
            else:
                files.append({
                    'name': item,
                    'path': os.path.join(site_path, item),
                    'size': os.path.getsize(item_path),
                    'type': 'file'
                })
        
        # Sort directories and files
        dirs.sort(key=lambda x: x['name'])
        files.sort(key=lambda x: x['name'])
        
        # Get parent directory
        parent_dir = os.path.dirname(site_path) if site_path else None
        
        return render_template('sites/file_manager.html', 
                              dirs=dirs, 
                              files=files, 
                              current_path=site_path,
                              full_path=full_path,
                              parent_dir=parent_dir)
                              
    except Exception as e:
        flash(f'Error accessing directory: {str(e)}', 'error')
        return redirect(url_for('sites.static_site'))

@sites_bp.route('/upload_file/<path:site_path>', methods=['POST'])
def upload_file(site_path):
    full_path = os.path.join('/var/www', site_path)
    
    # Security check to prevent directory traversal
    if not full_path.startswith('/var/www'):
        flash('Invalid path specified', 'error')
        return redirect(url_for('sites.static_site'))
    
    try:
        if 'file' not in request.files:
            flash('No file part in the request', 'error')
            return redirect(url_for('sites.file_manager', site_path=site_path))
        
        files = request.files.getlist('file')
        
        if not files or files[0].filename == '':
            flash('No files selected for upload', 'error')
            return redirect(url_for('sites.file_manager', site_path=site_path))
        
        successful_uploads = 0
        failed_uploads = 0
        
        for file in files:
            if file.filename:
                # Secure the filename to prevent path traversal
                filename = secure_filename(file.filename)
                file_path = os.path.join(full_path, filename)
                
                try:
                    file.save(file_path)
                    successful_uploads += 1
                except Exception as e:
                    flash(f'Error uploading {filename}: {str(e)}', 'error')
                    failed_uploads += 1
        
        if successful_uploads > 0:
            flash(f'Successfully uploaded {successful_uploads} file(s)', 'success')
        if failed_uploads > 0:
            flash(f'Failed to upload {failed_uploads} file(s)', 'error')
        
        return redirect(url_for('sites.file_manager', site_path=site_path))
    
    except Exception as e:
        flash(f'Error uploading files: {str(e)}', 'error')
        return redirect(url_for('sites.file_manager', site_path=site_path))

@sites_bp.route('/delete_file/<path:file_path>', methods=['POST'])
def delete_file(file_path):
    full_path = os.path.join('/var/www', file_path)
    
    # Security check to prevent directory traversal
    if not full_path.startswith('/var/www'):
        flash('Invalid path specified', 'error')
        return redirect(url_for('sites.static_site'))
    
    # Get the parent directory for redirect after deletion
    parent_dir = os.path.dirname(file_path)
    
    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
            flash(f'File deleted successfully', 'success')
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)
            flash(f'Directory deleted successfully', 'success')
        else:
            flash('File or directory not found', 'error')
        
        return redirect(url_for('sites.file_manager', site_path=parent_dir))
    
    except Exception as e:
        flash(f'Error deleting: {str(e)}', 'error')
        return redirect(url_for('sites.file_manager', site_path=parent_dir))

@sites_bp.route('/create_directory/<path:site_path>', methods=['POST'])
def create_directory(site_path):
    full_path = os.path.join('/var/www', site_path)
    
    # Security check to prevent directory traversal
    if not full_path.startswith('/var/www'):
        flash('Invalid path specified', 'error')
        return redirect(url_for('sites.static_site'))
    
    try:
        dir_name = request.form.get('dirname', '')
        if not dir_name:
            flash('Directory name is required', 'error')
            return redirect(url_for('sites.file_manager', site_path=site_path))
        
        # Secure the directory name
        dir_name = secure_filename(dir_name)
        new_dir_path = os.path.join(full_path, dir_name)
        
        if os.path.exists(new_dir_path):
            flash('Directory already exists', 'error')
            return redirect(url_for('sites.file_manager', site_path=site_path))
        
        os.makedirs(new_dir_path)
        flash(f'Directory {dir_name} created successfully', 'success')
        return redirect(url_for('sites.file_manager', site_path=site_path))
    
    except Exception as e:
        flash(f'Error creating directory: {str(e)}', 'error')
        return redirect(url_for('sites.file_manager', site_path=site_path))

@sites_bp.route('/download_file/<path:file_path>')
def download_file(file_path):
    directory = os.path.join('/var/www', os.path.dirname(file_path))
    filename = os.path.basename(file_path)
    
    # Security check to prevent directory traversal
    if not directory.startswith('/var/www'):
        flash('Invalid path specified', 'error')
        return redirect(url_for('sites.static_site'))
    
    try:
        return send_from_directory(directory, filename, as_attachment=True) 
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('sites.static_site')) 

@sites_bp.route('/get_static_site_path/<config_name>')
def get_static_site_path(config_name):
    """
    Get the static site path for a given configuration.
    Returns JSON with the site path if it is a static site.
    """
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    content = nginx_manager.get_config_content(config_name)
    
    if not content:
        return jsonify({'success': False, 'message': 'Configuration not found'})
    
    # Simple parsing to find the root directive in a server block
    root_path = None
    in_server_block = False
    
    for line in content.splitlines():
        line = line.strip()
        
        if line.startswith('server {'):
            in_server_block = True
        elif line == '}' and in_server_block:
            in_server_block = False
        elif in_server_block and line.startswith('root '):
            # Extract the root path
            parts = line.split()
            if len(parts) >= 2:
                root_path = parts[1].rstrip(';')
                break
    
    if root_path and root_path.startswith('/var/www/'):
        site_path = root_path[9:].rstrip('/')  # Remove the '/var/www/' prefix
        return jsonify({
            'success': True, 
            'is_static_site': True,
            'site_path': site_path
        })
    
    return jsonify({
        'success': True,
        'is_static_site': False
    })

@sites_bp.route('/static_upload', methods=['POST'])
def static_upload():
    site_name = request.form.get('site_name', '')
    
    if not site_name:
        flash('No site selected', 'error')
        return redirect(url_for('sites.static_site'))
    
    # Secure the site name to prevent path traversal
    site_name = secure_filename(site_name)
    upload_dir = os.path.join('/var/www', site_name)
    
    # Make sure the directory exists
    if not os.path.exists(upload_dir):
        try:
            os.makedirs(upload_dir, exist_ok=True)
            flash(f'Created directory for {site_name}', 'success')
        except Exception as e:
            flash(f'Error creating directory: {str(e)}', 'error')
            return redirect(url_for('sites.static_site'))
    
    # Check if the post request has the file parts
    if 'files' not in request.files:
        flash('No files selected', 'error')
        return redirect(url_for('sites.static_site'))
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        flash('No files selected', 'error')
        return redirect(url_for('sites.static_site'))
    
    # Process each file
    successful_uploads = 0
    failed_uploads = 0
    
    for file in files:
        if file.filename:
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                successful_uploads += 1
            except Exception as e:
                flash(f'Error uploading {file.filename}: {str(e)}', 'error')
                failed_uploads += 1
    
    if successful_uploads > 0:
        flash(f'Successfully uploaded {successful_uploads} file(s) to {site_name}', 'success')
    if failed_uploads > 0:
        flash(f'Failed to upload {failed_uploads} file(s)', 'error')
    
    return redirect(url_for('sites.file_manager', site_path=site_name)) 