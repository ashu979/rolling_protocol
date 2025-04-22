# documents/utils.py

import jwt
import uuid
from datetime import datetime, timedelta

SECRET_KEY = 'mes-dolvi-rolling-protocol'

def create_one_time_token(doc_title):
    payload = {
        'doc_title': doc_title,
        'exp': datetime.utcnow() + timedelta(minutes=10),
        'jti': str(uuid.uuid4())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
