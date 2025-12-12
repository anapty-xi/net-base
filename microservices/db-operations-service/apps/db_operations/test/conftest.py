from sys import path

path.insert(0, '/home/anapty-xi/net-base/microservices/db-operation-service')

try: 
    import apps
except Exception as e:
    raise e