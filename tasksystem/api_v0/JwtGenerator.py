
'''
Class created for JWT generator logic
creates the token
@Author : Lija G
@Since : 24-01-2020
'''


from datetime import datetime,timedelta
import jwt

format = "%Y-%m-%d %H:%M:%S"
algorithm='HS256'

def jwtGenerator(user_id, is_admin, jwt_secret, jwt_ttl, type):
    currentTime = datetime.now()
    time = currentTime.strftime(format)
    if jwt_ttl >= 0:
        expTime = currentTime + timedelta(seconds = jwt_ttl)
        expAt = expTime.strftime(format)
        actualExp = datetime.strptime(expAt,format)
    payload = {"user_id" : user_id, "is_admin":is_admin, "type" : type, "issued_at": time, "exp" : actualExp.timestamp()}
    jwtToken = jwt.encode(payload, jwt_secret, algorithm)
    return jwtToken.decode()

def passwordToken(profileId, jwtSecret, jwtTtl):
    currentTime = datetime.now()
    time = currentTime.strftime(format)
    if (jwtTtl >= 0):
        expTime = currentTime + timedelta(milliseconds=jwtTtl)
        # print("expTime b4 setting:" + str(expTime))
    payload = {"profile_id": profileId,  "issued_at": time, "exp": expTime}
    jwtToken = jwt.encode(payload, jwtSecret, algorithm)
    return jwtToken.decode()



