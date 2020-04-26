# TaskManagement
Employee Task Management System
1. clone or down load the project
2. open tasksystem in corresponding ide.
3. replace appropriate values for DATABASES, EMAIL_HOST_USER , EMAIL_HOST_PASSWORD  in settings.py file (tasksystem\tasksytem\settings.py)
4. replace the values in config.json also(tasksystem\api_v0\config.json)
5. install the requirements using pip install -r /path/to/requirements.txt
6. create a database in the corresponding db with name in settings file( mysql command -create database task-system)
6. run migration script(python manage.py migrate)
7. run the server by activating virtual env 
source venv/bin/activate
python manage.py runserver


# Run the schedular

1.go to the path of schedular.py
2. screen -r 
3. run the file by 
python schedular.py <config file name with path)
