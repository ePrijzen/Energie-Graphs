import os
import json
import logging
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class LeverancierRequests:

    def __init__(self, config:dict={}, bearer_key:str="") -> None:
        try:
            if config is None:
                raise Exception('No config!')

            self.ip = config["api"]["ip"]
            self.port = config["api"]["port"]
            self.bearer_key = bearer_key
        except Exception as e:
            log.critical(e, exc_info=True)

    def leveranciers(self, fromdate:str="", kind:str="", country:str=""):
        try:
            payload = json.dumps({"datum": fromdate, "kind": kind, "country": country})
            return self.leverancier_api_call(payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)

    def leverancier_api_call(self, payload:json = {})->dict:
        try:
            reqUrl = f"http://{self.ip}:{self.port}/energy/api/v1.0/leveranciers"
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_key}"
            }
            response = requests.request("GET", reqUrl, data=payload, headers=headersList, timeout=10)
            if response.status_code == 200:
                return  response.json()

            return {}
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}
