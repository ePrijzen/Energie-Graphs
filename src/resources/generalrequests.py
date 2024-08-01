import os
import logging
import hashlib
import json
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class GeneralRequests:

    def __init__(self, config:dict={}) -> None:
        try:
            if config is None:
                raise Exception('No config!')

            self.ip = config["api"]["ip"]
            self.port = config["api"]["port"]
            self.bearer_key = None
        except Exception as e:
            log.critical(e, exc_info=True)



    def get_password(self, password:str=None, salt:str=None)->str:
        try:
            if password is None or salt is None:
                raise Exception('Geen wachtwoord of salt?')
            # Adding salt at the last of the password
            salted_password = password+salt
            # Encoding the password
            hashed_password = hashlib.md5(salted_password.encode())

            return hashed_password.hexdigest()
        except Exception as e:
            log.critical(e, exc_info=True)
            return ""

    def get_bearer_key(self, email:str="", password:str="")->str:
        try:
            if password is None:
                raise Exception('Geen wachtwoord?')

            payload = json.dumps({"email": email, "password": password})
            reqUrl = f"http://{self.ip}:{self.port}/energy/api/v1.0/login"
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json"
            }
            response = requests.request("POST", reqUrl, data=payload,  headers=headersList, timeout=5)
            if response.status_code == 200:
                mjson = response.json()
                self.bearer_key = mjson['access_token']
                return self.bearer_key
            return ""
        except Exception as e:
            log.critical(e, exc_info=True)
            return ""
