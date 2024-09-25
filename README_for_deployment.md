
# STEPS FOR CLONING 
```
cd existing_folder
git clone https://github.com/ExtGroupJs/supermario_shop.git

```

# STEPS FOR DEVELOPING
0. cd supermario_shop

1.  when the code is already cloned, create a python virtual enviroment (using currently python 3.11):
python3 -m venv venv

2. Activate virtual enviroment:
source /venv/bin/activate # for linux

3. Install required packages running in the console:
pip install -r deploy_requirements.txt

4. Make a copy of REFERENCE.env in the same directory and remove the filename. Finally the file should exists with the name: .env
cp project_site/.REFERENCE.env project_site/.env

5. Run migrations (with this we have created a superuser):
python manage.py migrate

7. collect_statics:
python manage.py collectstatic


* SETUP GUNICORN

sudo nano /etc/systemd/system/gunicorn_supermario_shop.service

#####
[Unit]
Description=supermario_shop daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/home/projects/supermario_shop
ExecStart=/home/projects/supermario_shop/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/projects/supermario_shop/project_site/project_site.sock project_site.wsgi:application

[Install]
WantedBy=multi-user.target
#####

sudo systemctl start gunicorn_supermario_shop.service

sudo systemctl enable gunicorn_supermario_shop.service

sudo systemctl status gunicorn_supermario_shop.service

- if some problem happened: 
sudo journalctl -u gunicorn
- If you make changes to the /etc/systemd/system/gunicorn_supermario_shop.service file, reload the daemon:
sudo systemctl daemon-reload
sudo systemctl restart gunicorn_supermario_shop.service

* SETUP NGINX
sudo apt install nginx

sudo nano /etc/nginx/sites-available/projects

###
server {
	listen 80;
	server_name 217.76.49.67;
	location = /favicon.ico { access_log off; log_not_found off; }
	location /static_output/ {
			root /home/projects/supermario_shop;
	}
	location /media/ {
			root /home/projects/supermario_shop;
	}
	location / {
		include proxy_params;
		proxy_pass  http://unix:///home/projects/supermario_shop/project_site/project_site.sock;
		#proxy_redirect off;
	}
	
}
###

sudo ln -s /etc/nginx/sites-available/projects /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl status nginx