import os

from dotenv import load_dotenv
load_dotenv()

def get_secret(secret_name):
    '''
    Получает секреты Docker
    '''
    path = str(os.getenv(secret_name))
    with open (path) as f:
        secret_file = f.readline()

    return secret_file.split('=', 1)[1].strip()