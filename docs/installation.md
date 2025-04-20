# Установка и настройка

## Установка зависимостей

1. Установите Python 3.7 или выше
2. Установите Nginx
3. Установите необходимые системные пакеты:

```bash
# Для Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-venv nginx

# Для CentOS/RHEL
sudo yum install python3 nginx
```

## Установка приложения

1. Клонируйте репозиторий:

```bash
git clone https://github.com/yourusername/nginx-web-panel.git
cd nginx-web-panel
```

2. Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Настройте приложение:

Отредактируйте файл `app.py` и укажите путь к директории конфигурации Nginx:

```python
app.config['NGINX_CONFIG_DIR'] = '/etc/nginx'  # Измените на ваш путь
```

## Запуск приложения

### Разработка

Для запуска в режиме разработки:

```bash
python app.py
```

Приложение будет доступно по адресу: http://localhost:5000

### Производство

Для производственного использования рекомендуется использовать Gunicorn:

1. Установите Gunicorn:

```bash
pip install gunicorn
```

2. Запустите с Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Настройте обратный прокси (Nginx) для обслуживания приложения:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Настройка прав доступа

Убедитесь, что пользователь, от имени которого запускается приложение, имеет необходимые права:

```bash
# Добавьте пользователя в группу www-data (Ubuntu/Debian)
sudo usermod -a -G www-data your_user

# Или в группу nginx (CentOS/RHEL)
sudo usermod -a -G nginx your_user
```

## Настройка systemd (опционально)

Для автоматического запуска приложения при загрузке системы:

1. Создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/nginx-web-panel.service
```

2. Добавьте следующее содержимое:

```ini
[Unit]
Description=Nginx Web Panel
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/nginx-web-panel
Environment="PATH=/path/to/nginx-web-panel/venv/bin"
ExecStart=/path/to/nginx-web-panel/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

3. Включите и запустите сервис:

```bash
sudo systemctl enable nginx-web-panel
sudo systemctl start nginx-web-panel
``` 