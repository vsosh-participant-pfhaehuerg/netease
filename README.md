# Nginx Web Panel

A web-based GUI panel for managing Nginx web server configurations, built with Python and Flask.

## Features

- Create and manage Nginx configuration files
- Generate configurations for different use cases:
  - Proxy servers
  - Static file serving
  - SSL/TLS configurations
  - Load balancing
  - PHP-FPM and more
- Security validation of configurations
- Enable/disable configurations
- Test and reload Nginx configurations
- Modern, responsive UI

## Prerequisites

- Python 3.7 or higher
- Nginx web server installed
- Appropriate permissions to read/write Nginx configuration directories

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/nginx-web-panel.git
cd nginx-web-panel
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Configure the application:

Edit the `app.py` file and update the `NGINX_CONFIG_DIR` setting to point to your Nginx configuration directory:

```python
app.config['NGINX_CONFIG_DIR'] = '/etc/nginx'  # Change to your Nginx config path
```

## Running the Application

1. Start the web panel:

```bash
python app.py
```

2. Access the web interface at http://localhost:5000

## For Production Use

For production deployment, it's recommended to use a WSGI server like Gunicorn:

1. Install Gunicorn:

```bash
pip install gunicorn
```

2. Run with Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Configure a reverse proxy (Nginx itself) to serve the application.

## Security Considerations

- The application needs permissions to read and write Nginx configuration files
- On production systems, ensure proper authentication is added
- Restrict access to the panel to authorized users only
- Consider running the app with a dedicated user with limited permissions

## License / Лицензия

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Этот проект распространяется под лицензией MIT - подробности в файле [LICENSE](LICENSE).

### MIT License Summary / Краткое описание лицензии MIT

The MIT License is a permissive free software license that:
- Allows commercial use
- Allows modifications
- Allows distribution
- Allows private use
- Includes liability limitation
- Includes warranty limitation

Лицензия MIT - это разрешительная лицензия свободного программного обеспечения, которая:
- Разрешает коммерческое использование
- Разрешает модификации
- Разрешает распространение
- Разрешает частное использование
- Включает ограничение ответственности
- Включает ограничение гарантий 