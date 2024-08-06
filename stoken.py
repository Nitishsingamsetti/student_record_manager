from itsdangerous import URLSafeTimedSerializer
from key import salt,secret_key

def token(data):
    serializer=URLSafeTimedSerializer(secret_key)
    return serializer.dumps(data,salt=salt)
