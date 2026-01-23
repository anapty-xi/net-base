import os

from dotenv import load_dotenv
load_dotenv()

def get_secret(secret_name):
    path = str(os.getenv(secret_name))
    with open (path) as f:
        secret_file = f.readline().strip()

    return secret_file.split('=', 1)[1]