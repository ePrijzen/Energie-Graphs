import os
import logging
import json
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class EnergieRequests:

    def __init__(self, config:dict={}, bearer_key:str="") -> None:
        try:
            if not config:
                raise Exception('No config!')

            self.ip = config["api"]["ip"]
            self.port = config["api"]["port"]
            self.bearer_key = bearer_key
        except Exception as e:
            log.critical(e, exc_info=True)

    def all_prices(self, fromdate:str="", todate:str="", fromtime:str="12:00", kind:str="g", country:str="NL", dutch_floats:bool=False):
        try:
            payload = json.dumps({"fromdate": fromdate, "todate":todate, "fromtime": fromtime, "dutch_floats": dutch_floats, "average": False, "kind": kind, "country":country})
            return self.prices_api_call(payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)

    def avg_prices(self, datum:str="", tijd:str="", kind:str="e"):
        try:
            payload = json.dumps({"fromdate": datum, "fromtime": tijd, "dutch_floats": False, "average": True, "kind": kind})
            return self.prices_api_call(payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)

    def avg_prices_per_month(self, fromdate:str="", todate:str="", kind:str="e", country:str="NL"):
        try:
            payload = json.dumps({"fromdate": fromdate, "todate": todate, "dutch_floats": False, "average": True, "kind": kind, "country": country, "group_by": "ym"})
            return self.prices_api_call(payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)

    def avg_from_to_prices(self, fromdate:str="", fromtime:str="", todate:str="", kind:str="e", country:str="NL", group_by:str=""):
        try:
            payload = json.dumps({"fromdate": fromdate, "todate": todate, "fromtime": fromtime, "dutch_floats": False, "average": True, "kind": kind, "country": country, 'group_by': group_by})
            return self.prices_api_call(payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)

    def get_prices(self, datum:str="", tijd:str="", kind:str="", user_id:int=None, lowest:bool = False, highest:bool = False, country:str="NL")->dict:
        try:
            payload = json.dumps({"fromdate": datum, "fromtime": tijd, "dutch_floats": False, "kind": kind,
                                  "user_id": user_id, "lowest":lowest, "highest":highest, "country": country})
            return self.prices_api_call(payload=payload)
        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    def prices_api_call(self, payload:str)->dict:
        try:
            reqUrl = f"http://{self.ip}:{self.port}/energy/api/v1.0/prices"
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