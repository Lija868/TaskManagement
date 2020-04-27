import uuid

from django.shortcuts import render

# Create your views here.

import hashlib
from datetime import time, datetime
from threading import Thread

import bcrypt
from django.db.models import Q

# Create your views here.
# -*- coding: utf-8 -*-
from api_v0 import serializers
from api_v0.JwtGenerator import jwtGenerator
from api_v0.JwtValidator import jwtValidator
from api_v0.authentication import TokensAuthentication
from api_v0.models import *
from api_v0.pagination import CustomPageNumberPagination
from api_v0.utilities import *
from tasksystem import settings

""" API v0 views."""

from django.views.decorators.cache import cache_control

from rest_framework import response
from rest_framework import schemas
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication

from rest_framework.response import Response


def schema_view(request):
    """Return v0 API schema."""
    generator = schemas.SchemaGenerator(
        title="True Caller API v0", urlconf="truecaller.api_v0.urls", url="/v0"
    )
    schema = generator.get_schema(request)
    return response.Response(schema)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class RegisterViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        response = {}
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        phone_number = request.data.get("phone_no")
        password = request.data.get("password")
        is_admin = request.data.get("is_admin")

        # display what are the fields which tent to empty.
        validatations = []
        validatations = validateNullOrEmpty(first_name, 702, "First name" , validatations)
        validatations = validateNullOrEmpty(last_name, 703, "Last name" , validatations)
        validatations = validateNullOrEmpty(email, 705, "Email", validatations)
        validatations = validateNullOrEmpty(password, 706, "Password", validatations)

        if len(validatations) > 0:
            resp = {}
            resp["code"] = 600
            resp["validations"] = validatations
            return Response(resp)

        if phone_number:
            if not validate_phone(phone_number):
                return Response({"code": 707, "message": "phone number is not valid"})
        if not validate_email(email):
            return Response({"code": 708, "message": "Email is not valid"})
        if not validate_password(password):
            return Response({"code": 709, "message": "Email is not valid"})



        full_name = first_name + " "+ last_name

        user_obj = User.objects.filter(email=email).count()
        if user_obj >= 1:
            return Response({"code": 710, "message": "Email is already registered, try another Email."})
        else:
            try :
                user_id = hashlib.md5(email.encode() + (str(time)).encode()).hexdigest()
                password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

                user_obj = User.objects.create(
                    user_id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    password_hash = password_hash,
                    email=email,
                    phone_number=phone_number,
                    is_admin = is_admin

                )
                response["code"] = 200
                response["message"] = "ok"
                response["user_id"] = user_obj.user_id
                return Response(response)
            except Exception as e:
                return Response({"code": 114, "message": "Unable to process the request"})

class LoginViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = ()
    authentication_classes = ()

    def create(self, request, *args, **kwargs):

        email = request.data.get("email")
        password = request.data.get("password")
        # display what are the fields which tent to empty.
        validatations = []
        validatations = validateNullOrEmpty(email, 705, "Email", validatations)
        validatations = validateNullOrEmpty(password, 706, "Password", validatations)
        if len(validatations) > 0:
            resp = {}
            resp["code"] = 600
            resp["validations"] = validatations
            return Response(resp)

        try :

            user_obj = User.objects.get(email=email, is_deleted = False)
        except:
            return Response({"code":711,"message":"Invalid Credentials"})

        try:
            password_hash = user_obj.password_hash
            matched = bcrypt.checkpw(password.encode(), password_hash.encode())

            if (not matched):
                return Response({"code": 711, "message": "invalid credentials"})

            access_token = jwtGenerator(user_obj.user_id, user_obj.is_admin, settings.JWT_SECRET, settings.TOKEN_EXPIRY, "access")
            refresh_token = jwtGenerator(user_obj.user_id, user_obj.is_admin,  settings.JWT_SECRET, settings.REFRESH_TOKEN_EXPIRY, "refresh")
            Token.objects.filter(user_id=user_obj).update(is_expired = 1)

            Token.objects.update_or_create(
                user_id=user_obj,
                access_token=access_token,
                refresh_token=refresh_token,
                defaults={"updated_on" : datetime.datetime.now()}
            )

            response_obj = {}
            response_obj["message"] = "ok"
            response_obj["code"] = 200
            response_obj["access_token"] = access_token
            response_obj["refresh_token"] = refresh_token

            return Response(response_obj)
        except Exception as e:
            return Response({"code": 114, "message": "Unable to process the request"})

# class to see any users details passing id
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    authentication_classes = [
       TokensAuthentication
    ]
    permission_classes = ()

    def get_queryset(self):
        user_id = self.kwargs.get("pk", None)
        user_data = User.objects.filter(user_id=user_id).values()
        return user_data



class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    authentication_classes = [
        TokensAuthentication
    ]
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):

        task_id = str(self.kwargs.get("pk", None))
        task_data = Task.objects.filter(id=task_id).values()
        return task_data

    def filter_queryset(self, queryset):
        """Combined filter queries"""
        task_id = self.kwargs.get("pk", None)
        task_name = self.request.query_params.get("task_name", None)
        task_description = self.request.query_params.get("task_description", None)
        assigned_to = self.request.query_params.get("assigned_to", None)
        sort_by = self.request.query_params.get("order_by", None)
        order = self.request.query_params.get("order", "asc")

        filters = Q()
        filters &= Q(is_deleted=False)

        if task_id:
            filters &= Q(id=task_id)
        if task_name:
            filters &= Q(task_name__icontains=task_name)
        if task_description:
            filters &= Q(task_description__icontains=task_description)
        if assigned_to:
            filters &= Q(assigned_to=assigned_to)

        queryset = Task.objects.filter(filters)

        queryset = queryset.filter(filters)
        if sort_by :
            if order == "asc":
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by(sort_by).reverse()

        return queryset

    @cache_control(max_age=0)
    def list(self, request, *args, **kwargs):
        """List a queryset.

        Overrides rest_framework.mixins.ListModelMixin.list() to add a
        cache_control header.
        """

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"result":serializer.data})


    def create(self, request, *args, **kwargs):
        task_name = request.data.get("task_name")
        task_description = request.data.get("task_description")
        assigned_to = request.data.get("assigned_to")
        token_id = request.headers.get("Authorization", "")
        payload = {}
        if not task_name:
            return Response({"code": 712, "message": "Task name cannot be null or empty"})
        if not assigned_to:
            return Response({"code": 713, "message": "Assignee cannot be null or empty"})

        try:
            payload = jwtValidator(token_id)
            Token.objects.get(access_token=token_id, is_expired = 0)
        except:
            return Response({"code": 401, "message": "Expired or Invalid Token"})
        try:
            user_id = payload["user_id"]
            is_admin = payload["is_admin"]
            if not is_admin:
                return Response({"code": 206, "message": "You don't have permission to perform this action"})

            user_obj = User.objects.get(user_id = assigned_to, is_deleted = 0)
            task_id = hashlib.md5(uuid.uuid4().hex.encode() + (str(datetime.datetime.now())).encode()).hexdigest()

            Task.objects.create(
                id = task_id,
                assigned_to=user_obj,
                task_name=task_name,
                task_description=task_description,
                created_by=user_id,
                updated_by=user_id)

            t = Thread(target=send_mail_user, args=(user_obj.email, user_obj.full_name))
            t.start()
            resp = {}
            resp["code"] = 200
            resp["message"] = "OK"
            resp["task_id"] = task_id
            return Response(resp)
        except Exception as e:
            return Response({"code": 114, "message": "Unable to process the request"})

    def update(self, request, *args, **kwargs):
        task_id = self.kwargs.get("pk")
        start_task = request.data.get("is_task_start", True)
        expected_completetion_time = request.data.get("expected_completetion_time" )

        token_id = request.headers.get("Authorization", "")
        payload = {}


        try:
            payload = jwtValidator(token_id)
            Token.objects.get(access_token=token_id, is_expired=0)
        except:
            return Response({"code": 401, "message": "Expired or Invalid Token"})
        try:
            user_id = payload["user_id"]

            task_exists = Task.objects.filter(id=task_id, assigned_to = user_id, is_deleted = 0)
            if not task_exists:
                resp = {"code": 204, "message": "Task is not existing in the system"}
                return Response(resp)

            if start_task:

                Task.objects.filter(id=task_id, assigned_to = user_id, is_deleted = 0).update(
                    task_start_time=datetime.datetime.now(),
                    expected_completetion_time = convertStrTime(expected_completetion_time),
                    updated_by = user_id, updated_on = datetime.datetime.now()
                )
            else:
                Task.objects.filter(id=task_id, assigned_to = user_id, is_deleted = 0).update(
                    actual_completetion_time=datetime.datetime.now(), updated_by = user_id, updated_on = datetime.datetime.now()
                )

            resp = {}
            resp["code"] = 200
            resp["message"] = "OK"
            return Response(resp)
        except Exception as e:
            return Response({"code": 114, "message": "Unable to process the request"})


class LogoutViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = ()

    def create(self, request,  *args, **kwargs):
        token_id = request.headers.get("Authorization", "")
        try:
            jwtValidator(token_id)
            Token.objects.get(access_token=token_id, is_expired=0)
        except:
            return Response({"code": 401, "message": "Expired or Invalid Token"})
        try:
            token_obj = Token.objects.get(access_token=token_id)
            token_obj.is_expired = 1
            token_obj.save()
            return Response({"code": 200, "message": "ok"})
        except:
            return Response({"code": 114, "message": "Unable to process the request"})

