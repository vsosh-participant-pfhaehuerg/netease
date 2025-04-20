# Устранение неполадок

## Общие проблемы

### Приложение не запускается

1. Проверьте версию Python:
   ```bash
   python --version
   ```
   Должна быть 3.7 или выше.

2. Проверьте установленные зависимости:
   ```bash
   pip list
   ```

3. Проверьте права доступа:
   ```bash
   ls -la /etc/nginx
   ```

### Ошибки при входе в систему

1. Проверьте файл конфигурации:
   ```bash
   cat ~/.oshfask/config.json
   ```

2. Попробуйте сбросить пароль:
   ```bash
   rm ~/.oshfask/config.json
   ```

3. Проверьте логи:
   ```bash
   tail -f /var/log/nginx-web-panel.log
   ```

## Проблемы с конфигурациями

### Ошибки синтаксиса

1. Проверьте конфигурацию:
   ```bash
   nginx -t
   ```

2. Посмотрите последние изменения:
   ```bash
   ls -la /etc/nginx/conf.d/
   ```

3. Восстановите из резервной копии:
   ```bash
   cp /etc/nginx/conf.d/backup/latest.conf /etc/nginx/conf.d/
   ```

### Проблемы с правами доступа

1. Проверьте владельца файлов:
   ```bash
   ls -la /etc/nginx/
   ```

2. Измените права:
   ```bash
   sudo chown -R www-data:www-data /etc/nginx/
   sudo chmod -R 755 /etc/nginx/
   ```

## Проблемы с Nginx

### Nginx не перезапускается

1. Проверьте статус:
   ```bash
   systemctl status nginx
   ```

2. Посмотрите логи:
   ```bash
   journalctl -u nginx
   ```

3. Проверьте конфигурацию:
   ```bash
   nginx -t
   ```

### Ошибки в работе сайтов

1. Проверьте конфигурацию сайта:
   ```bash
   cat /etc/nginx/sites-available/your-site.conf
   ```

2. Проверьте логи:
   ```bash
   tail -f /var/log/nginx/error.log
   ```

3. Проверьте доступность:
   ```bash
   curl -I http://your-site.com
   ```

## Проблемы с производительностью

### Высокая нагрузка на CPU

1. Проверьте процессы:
   ```bash
   top
   ```

2. Посмотрите использование памяти:
   ```bash
   free -m
   ```

3. Проверьте логи:
   ```bash
   tail -f /var/log/nginx/access.log
   ```

### Медленная работа интерфейса

1. Проверьте сетевые задержки:
   ```bash
   ping your-server
   ```

2. Проверьте использование памяти:
   ```bash
   htop
   ```

3. Проверьте логи приложения:
   ```bash
   tail -f /var/log/nginx-web-panel.log
   ```

## Восстановление после сбоев

### Восстановление конфигурации

1. Найдите последнюю резервную копию:
   ```bash
   ls -la /etc/nginx/conf.d/backup/
   ```

2. Восстановите конфигурацию:
   ```bash
   cp /etc/nginx/conf.d/backup/latest.conf /etc/nginx/conf.d/
   ```

3. Перезапустите Nginx:
   ```bash
   systemctl restart nginx
   ```

### Восстановление базы данных

1. Найдите резервную копию:
   ```bash
   ls -la ~/.oshfask/backup/
   ```

2. Восстановите данные:
   ```bash
   cp ~/.oshfask/backup/latest.json ~/.oshfask/config.json
   ```

3. Перезапустите приложение:
   ```bash
   systemctl restart nginx-web-panel
   ```

## Получение помощи

### Сбор информации для отчета

1. Соберите системную информацию:
   ```bash
   uname -a
   python --version
   nginx -v
   ```

2. Соберите логи:
   ```bash
   journalctl -u nginx > nginx.log
   journalctl -u nginx-web-panel > panel.log
   ```

3. Соберите конфигурации:
   ```bash
   cp /etc/nginx/nginx.conf nginx.conf
   cp ~/.oshfask/config.json panel.json
   ```

### Отправка отчета

1. Создайте архив:
   ```bash
   tar -czf report.tar.gz *.log *.conf *.json
   ```

2. Отправьте на почту поддержки:
   ```bash
   mail -s "Отчет о проблеме" support@example.com < report.tar.gz
   ``` 