from django.db import models

# Create your models here.

from django.db import models

class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=200, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)
    is_admin = models.BooleanField(default=False)
    password_hash = models.CharField(max_length=1000)
    email = models.EmailField(db_index=True,  unique=True,max_length=70, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Task(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    assigned_to = models.ForeignKey(User,on_delete=models.CASCADE)
    task_name = models.CharField(max_length=200)
    task_description = models.TextField()
    task_start_time = models.DateField(null=True)
    expected_completetion_time = models.DateField(null=True)
    actual_completetion_time = models.DateField(null=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=200)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=200)


class Token(models.Model):
    user_id = models.ForeignKey(User, blank=True,null=True, on_delete=models.DO_NOTHING)
    refresh_token = models.TextField( blank=True, null=True)
    access_token = models.TextField( blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_expired = models.BooleanField(default=False)

