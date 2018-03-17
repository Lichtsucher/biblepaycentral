from fabric.api import local

def devel_celery():
    local("./env/bin/celery -A biblepaycentral worker -Q celery,standard -l INFO")
    
def devel_server():
    local("./env/bin/python manage.py runserver 0.0.0.0:8080")

