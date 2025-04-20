import os
import json
import hashlib
from pathlib import Path

class AuthManager:
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser('~'), '.oshfask')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Создает директорию конфигурации, если она не существует"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        if not os.path.exists(self.config_file):
            self._save_config({'password_hash': None, 'setup_complete': False})

    def _save_config(self, config):
        """Сохраняет конфигурацию в файл"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f)

    def _load_config(self):
        """Загружает конфигурацию из файла"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'password_hash': None, 'setup_complete': False}

    def set_password(self, password):
        """Устанавливает новый пароль"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        config = self._load_config()
        config['password_hash'] = password_hash
        self._save_config(config)

    def verify_password(self, password):
        """Проверяет правильность пароля"""
        config = self._load_config()
        if not config['password_hash']:
            return False
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == config['password_hash']

    def is_setup_complete(self):
        """Проверяет, завершена ли начальная настройка"""
        config = self._load_config()
        return config.get('setup_complete', False)

    def complete_setup(self):
        """Отмечает начальную настройку как завершенную"""
        config = self._load_config()
        config['setup_complete'] = True
        self._save_config(config) 