import os
import logging
import hashlib
import json
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class BelastingRequests:

    def __init__(self, config:dict={}, bearer_key:str="") -> None:
        try:
            if not config:
                raise Exception('No config!')

            self.ip = config["api"]["ip"]
            self.port = config["api"]["port"]
            self.bearer_key = bearer_key
        except Exception as e:
            log.critical(e, exc_info=True)

    @staticmethod
    def split_belasting(belastingen:dict={})->dict:
        try:
            if not belastingen:
                raise Exception("geen data of Belasting")
            new_data_set = {}
            for belasting in belastingen:
                new_data_set[belasting['kind']] = {'btw': belasting['btw'], 'opslag': round(belasting['opslag'],3), 'ode': round(belasting['ode'],3),
                             'eb': round(belasting['eb'],3), 'datum': belasting['datum']}

            return new_data_set
        except (Exception, KeyError) as e:
            log.warning(f"{e} | {belastingen}", exc_info=True)
            return {}

    def belasting(self, fromdate:str="", fromtime:str="", kind:str="", country:str=""):
        try:
            payload = json.dumps({"datum": fromdate, "kind": kind,})
            return self.belasting_api_call(payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)

    def belasting_api_call(self, payload:str="")->dict:
        try:
            reqUrl = f"http://{self.ip}:{self.port}/energy/api/v1.0/belastingen"
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_key}"
            }
            response = requests.request("GET", reqUrl, data=payload, headers=headersList, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            log.error(e, exc_info=True)
            return {}