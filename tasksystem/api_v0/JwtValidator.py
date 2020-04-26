'''
Class created by JWT validator logic
decrypts the token and gives payload
if token expires it raises the exception
@Author : Lija G
@Since : 24-01-2020
'''

import jwt
from datetime import datetime
from django.conf import settings

format = "%Y-%m-%d %H:%M:%S"
jwtSecret = settings.JWT_SECRET
options = {
    'verify_exp': True
}


def jwtValidator(token):
    payLoad = jwt.decode(token, jwtSecret, algorithm="HS256", options=options)
    return payLoad
