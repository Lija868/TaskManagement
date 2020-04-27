import datetime
import re


from tasksystem import settings
from django.core.mail import send_mail
from django.template import loader

format = "%Y-%m-%d"


mobile_regex = re.compile("[+](0/91)?[7-9][0-9]{9}")
email_regex = "^[\\w!#$%&'*+/=?`{|}~^-]+(?:\\.[\\w!#$%&'*+/=?`{|}~^-]+)*@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,5}$"
password_pattern = "((?=.*[0-9])(?=.*[!@#$%&*s]).{6,20})"


def validate_email(email):
    return re.match(email_regex, email)


def validate_phone(mobile_no):
    return mobile_regex.match(mobile_no)

def validate_password(password):
    return re.match(password_pattern, password)



# method to validate null or empty check
def validateNullOrEmpty(input, code, field, error):
    d = {}
    if(type(input) == str):
        if(input is None or input ==""):
            d["message"] = field + " cannot be null or empty"
            d["code"] = code
            error.append(d)
    elif(type(input) == int):
            if (input == 0):
                d["message"] = field + " cannot be null or empty"
                d["code"] = code
                error.append(d)
    elif (type(input) == float):
        if (input == 0.0):
            d["message"] =  field + " cannot be null or empty"
            d["code"] = code
            error.append(d)
    else:
        if (input is None or input == "" or len(input) == 0):
            d["message"] =  field + " cannot be null or empty"
            d["code"] = code
            error.append(d)

    return error

def convertStrTime(time):
    newtime = datetime.datetime.strptime(time,format)
    return newtime


def send_mail_user(email, full_name):
    email_template_name = "api_v0/task_created.html"
    context = {
        "user": full_name,
        "email": email
    }
    subject = "Task "
    message = "You Have new Task"
    t = loader.get_template(email_template_name)
    html_message = t.render(context)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
        auth_user=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD,
        html_message=html_message,
    )


