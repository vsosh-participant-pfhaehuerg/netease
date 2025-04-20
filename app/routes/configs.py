from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash
import os
import validators

configs_bp = Blueprint('configs', __name__)

@configs_bp.route('/')
def index():
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    configs = nginx_manager.get_all_configs()
    enabled_configs = nginx_manager.get_enabled_configs()
    
    # Get static site paths for file manager links
    static_sites = {}
    for config in configs:
        content = nginx_manager.get_config_content(config)
        if content:
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
                site_path = root_path[9:]  # Remove the '/var/www/' prefix
                static_sites[config] = site_path
    
    return render_template('configs/index.html', 
                          configs=configs, 
                          enabled_configs=enabled_configs,
                          static_sites=static_sites)

@configs_bp.route('/new')
def new():
    return render_template('configs/new.html')

@configs_bp.route('/edit/<config_name>')
def edit(config_name):
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    content = nginx_manager.get_config_content(config_name)
    
    if content is None:
        flash('Configuration not found', 'error')
        return redirect(url_for('configs.index'))
    
    config_validator = current_app.config.get('CONFIG_VALIDATOR')
    issues = config_validator.validate_config(content)
    
    # Set edit mode to true
    edit_mode = True
    
    return render_template('configs/view.html', 
                          config_name=config_name, 
                          content=content,
                          issues=issues,
                          edit_mode=edit_mode)

@configs_bp.route('/view/<config_name>')
def view(config_name):
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    content = nginx_manager.get_config_content(config_name)
    
    if content is None:
        flash('Configuration not found', 'error')
        return redirect(url_for('configs.index'))
    
    config_validator = current_app.config.get('CONFIG_VALIDATOR')
    issues = config_validator.validate_config(content)
    
    # Default to view mode
    edit_mode = False
    
    return render_template('configs/view.html', 
                          config_name=config_name, 
                          content=content,
                          issues=issues,
                          edit_mode=edit_mode)

@configs_bp.route('/save', methods=['POST'])
def save():
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    
    config_name = request.form.get('config_name')
    content = request.form.get('content')
    
    if not config_name or not content:
        flash('Missing required fields', 'error')
        return redirect(url_for('configs.index'))
    
    # Ensure filename has .conf extension
    if not config_name.endswith('.conf'):
        config_name += '.conf'
    
    success = nginx_manager.save_config(config_name, content)
    
    if success:
        flash(f'Configuration {config_name} saved successfully', 'success')
        
        # Validate the configuration after saving
        config_validator = current_app.config.get('CONFIG_VALIDATOR')
        issues = config_validator.validate_config(content)
        
        if issues:
            issue_count = len(issues)
            high_count = len([i for i in issues if i.get('level') == 'high'])
            
            if high_count > 0:
                flash(f'Warning: {high_count} high severity issues found in configuration', 'warning')
            elif issue_count > 0:
                flash(f'Info: {issue_count} potential issues found in configuration', 'info')
    else:
        flash('Failed to save configuration', 'error')
    
    # Always redirect to view mode after saving
    return redirect(url_for('configs.view', config_name=config_name))

@configs_bp.route('/delete/<config_name>', methods=['POST'])
def delete(config_name):
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    success = nginx_manager.delete_config(config_name)
    
    if success:
        flash(f'Configuration {config_name} deleted successfully', 'success')
    else:
        flash('Failed to delete configuration', 'error')
    
    return redirect(url_for('configs.index'))

@configs_bp.route('/enable/<config_name>', methods=['POST'])
def enable(config_name):
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    success = nginx_manager.enable_config(config_name)
    
    if success:
        flash(f'Configuration {config_name} enabled successfully', 'success')
    else:
        flash('Failed to enable configuration', 'error')
    
    return redirect(url_for('configs.index'))

@configs_bp.route('/disable/<config_name>', methods=['POST'])
def disable(config_name):
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    success = nginx_manager.disable_config(config_name)
    
    if success:
        flash(f'Configuration {config_name} disabled successfully', 'success')
    else:
        flash('Failed to disable configuration', 'error')
    
    return redirect(url_for('configs.index'))

@configs_bp.route('/test', methods=['POST'])
def test():
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    success, output = nginx_manager.test_config()
    
    return jsonify({
        'success': success,
        'output': output
    })

@configs_bp.route('/reload', methods=['POST'])
def reload():
    nginx_manager = current_app.config.get('NGINX_MANAGER')
    success, output = nginx_manager.reload_nginx()
    
    return jsonify({
        'success': success,
        'output': output
    })

@configs_bp.route('/validate', methods=['POST'])
def validate():
    config_validator = current_app.config.get('CONFIG_VALIDATOR')
    content = request.form.get('content')
    
    if not content:
        return jsonify({
            'success': False,
            'issues': []
        })
    
    issues = config_validator.validate_config(content)
    
    return jsonify({
        'success': True,
        'issues': issues
    }) 