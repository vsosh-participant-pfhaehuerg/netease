import os
import re
import shutil
import subprocess
import nginx
from pathlib import Path

class NginxManager:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.sites_available = os.path.join(config_dir, 'sites-available')
        self.sites_enabled = os.path.join(config_dir, 'sites-enabled')
        
    def get_all_configs(self):
        """Get all available configuration files"""
        configs = []
        if os.path.exists(self.sites_available):
            configs = [f for f in os.listdir(self.sites_available) 
                      if os.path.isfile(os.path.join(self.sites_available, f))]
        return configs
    
    def get_enabled_configs(self):
        """Get all enabled configuration files"""
        enabled = []
        if os.path.exists(self.sites_enabled):
            for f in os.listdir(self.sites_enabled):
                if os.path.islink(os.path.join(self.sites_enabled, f)):
                    enabled.append(f)
        return enabled
    
    def get_config_content(self, config_name):
        """Get the content of a configuration file"""
        config_path = os.path.join(self.sites_available, config_name)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return f.read()
        return None
    
    def save_config(self, config_name, content):
        """Save a configuration file"""
        if not os.path.exists(self.sites_available):
            os.makedirs(self.sites_available)
            
        config_path = os.path.join(self.sites_available, config_name)
        with open(config_path, 'w') as f:
            f.write(content)
        return True
    
    def enable_config(self, config_name):
        """Enable a configuration by creating a symbolic link"""
        if not os.path.exists(self.sites_enabled):
            os.makedirs(self.sites_enabled)
            
        source = os.path.join(self.sites_available, config_name)
        target = os.path.join(self.sites_enabled, config_name)
        
        if not os.path.exists(source):
            return False
        
        if os.path.exists(target):
            os.remove(target)
            
        os.symlink(source, target)
        return True
    
    def disable_config(self, config_name):
        """Disable a configuration by removing the symbolic link"""
        target = os.path.join(self.sites_enabled, config_name)
        if os.path.exists(target):
            os.remove(target)
            return True
        return False
    
    def delete_config(self, config_name):
        """Delete a configuration file"""
        self.disable_config(config_name)
        config_path = os.path.join(self.sites_available, config_name)
        if os.path.exists(config_path):
            os.remove(config_path)
            return True
        return False
    
    def test_config(self):
        """Test the Nginx configuration"""
        try:
            result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def reload_nginx(self):
        """Reload Nginx to apply changes"""
        try:
            result = subprocess.run(['nginx', '-s', 'reload'], capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
            
    def create_proxy_config(self, server_name, proxy_pass, listen_port=80, ssl=False):
        """Create a proxy configuration"""
        conf = nginx.Conf()
        server = nginx.Server()
        server.add(
            nginx.Key('listen', str(listen_port)),
            nginx.Key('server_name', server_name)
        )
        
        location = nginx.Location('/')
        location.add(
            nginx.Key('proxy_pass', proxy_pass),
            nginx.Key('proxy_set_header', 'Host $host'),
            nginx.Key('proxy_set_header', 'X-Real-IP $remote_addr'),
            nginx.Key('proxy_set_header', 'X-Forwarded-For $proxy_add_x_forwarded_for'),
            nginx.Key('proxy_set_header', 'X-Forwarded-Proto $scheme')
        )
        
        server.add(location)
        conf.add(server)
        
        return nginx.dumps(conf)
    
    def create_static_config(self, server_name, root_path, listen_port=80, index='index.html'):
        """Create a static file serving configuration"""
        conf = nginx.Conf()
        server = nginx.Server()
        server.add(
            nginx.Key('listen', str(listen_port)),
            nginx.Key('server_name', server_name),
            nginx.Key('root', root_path),
            nginx.Key('index', index)
        )
        
        location = nginx.Location('/')
        location.add(
            nginx.Key('try_files', '$uri $uri/ =404')
        )
        
        server.add(location)
        conf.add(server)
        
        return nginx.dumps(conf) 