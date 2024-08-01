import os
import logging
import json
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class GenerationsRequests:

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
    def split_generations(generations:dict={})->dict:
        try:
            if not generations:
                raise Exception("geen data of generations")

            solar = {}
            w_on = {}
            w_off = {}
            generation = ""

            for generation in generations['data']:
                match generation['kind']:
                    case 's':
                        solar[generation['fromtime']]=  generation['mw']
                    case 'w_off':
                        w_off[generation['fromtime']] =  generation['mw']
                    case 'w_on':
                        w_on[generation['fromtime']] =  generation['mw']
                    case _:
                        log.error(f"Probleem met generation {generation}")

            return {'solar': solar, 'w_on':w_on,'w_off':w_off}
        except (Exception, KeyError) as e:
            log.warning(f"{e} | {generations['data']}", exc_info=True)
            return {}


    #king = s=solar w_off = wind offshore w_on = wind onshore
    def generations_by_date(self, fromdate:str="", fromtime:str="", kind:str="", country:str="NL"):
        try:
            payload = json.dumps({"fromdate": fromdate, "fromtime": fromtime, "kind": kind, "country":country})
            return self.generations_api_call(payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)

    def generations_api_call(self, payload:str="")->dict:
        try:
            reqUrl = f"http://{self.ip}:{self.port}/energy/api/v1.0/generation"
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