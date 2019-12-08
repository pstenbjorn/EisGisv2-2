import os

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or '8234729483OJOfj3L'
    UPLOAD_FOLDER = 'temp_file/'