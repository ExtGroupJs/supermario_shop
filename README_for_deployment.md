  

# STEPS FOR CLONING

## Connect to the server via ssh

Go to the home folder (this way we avoid permission issues with the services)

     cd ../home
    
## Update the server
    sudo apt-get update 
    sudo apt-get upgrade
    
##  Install git
    apt install git
    
## ## Create folder structure for projects
    mkdir projects   
*If you check with `ls`, it should show the newly created folder **projects***
    
 **Enter the folder** 

     cd projects

## Clone the project from the repository (using https has fewer issues)

    git clone https://github.com/ExtGroupJs/supermario_shop.git

 **Enter the folder** 

    cd supermario_shop
    
## Verify that the required version of Python (3.11) is installed on the system.
You can check by running `python3 --version`. If it’s not installed, you can install it by connecting with:

    sudo apt install python3.11

y luego 

    apt install python3.11-venv

## Create the virtual enviroment for python

     python3.11 -m venv venv

## Activate virtual enviroment:

    source /venv/bin/activate # for linux
 
## Install required packages running in the console:

    pip install -r deploy_requirements.txt

## Make a copy of REFERENCE.env in the same directory and remove the filename. Finally the file should exists with the name: .env

    cp project_site/.REFERENCE.env project_site/.env

### Run migrations (with this we have created a superuser):

    python manage.py migrate

### Collect static files:

    python manage.py collectstatic

## SETUP GUNICORN

     sudo nano /etc/systemd/system/gunicorn_supermario_shop.service

  
**This is the content:**

> #####
>  [Unit]
> Description=supermario_shop daemon
> After=network.target
> 
> [Service]
> User=root
> Group=www-data
> 
> WorkingDirectory=/home/projects/supermario_shop
> ExecStart=/home/projects/supermario_shop/venv/bin/gunicorn
> --access-logfile - --workers 3 --bind unix:/home/projects/supermario_shop/project_site/project_site.sock
> project_site.wsgi:application
> 
> [Install]
> WantedBy=multi-user.target

    sudo systemctl start gunicorn_supermario_shop.service
    sudo systemctl enable gunicorn_supermario_shop.service
    sudo systemctl status gunicorn_supermario_shop.service

**- If some problem happened:**

    sudo journalctl -u gunicorn

If you make changes to the `/etc/systemd/system/gunicorn_supermario_shop.service` file, reload the daemon:

    sudo systemctl daemon-reload
    sudo systemctl restart gunicorn_supermario_shop.service

  
## SETUP NGINX

    sudo apt install nginx
    sudo nano /etc/nginx/sites-available/projects

**This is the content:**

> server {
> listen 80;
> server_name marioautoparts.extgroup.org 217.76.49.67;
> location = /favicon.ico { access_log off; log_not_found off; }
> 
> location /static_output/ {
> root /home/projects/supermario_shop;
> }
> 
> location /media/ {
> root /home/projects/supermario_shop;
> }
> 
> location / {
> include proxy_params;
> 
> proxy_pass http://unix:///home/projects/supermario_shop/project_site/project_site.sock;
> 
> #proxy_redirect off;
>    }
> }

  **Final configurations**

    sudo ln -s /etc/nginx/sites-available/projects /etc/nginx/sites-enabled
    sudo nginx -t
    sudo systemctl restart nginx

  
  **Checking status**

    sudo systemctl status nginx
