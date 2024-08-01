import os
import logging
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class CountryRequests:

    def __init__(self, config:dict=None, bearer_key:str=None) -> None:
        try:
            if config is None:
                raise Exception('No config!')

            self.ip = config["api"]["ip"]
            self.port = config["api"]["port"]
            self.bearer_key = bearer_key
        except Exception as e:
            log.critical(e, exc_info=True)


    def countries_api_call(self)->dict:
        try:
            reqUrl = f"http://{self.ip}:{self.port}/energy/api/v1.0/countries"
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_key}"
            }
            response = requests.request("GET", reqUrl,  headers=headersList, timeout=10)
            if response.status_code == 200:
                country_data = response.json()
                countries = {}
                for country in country_data['data']:
                    countries[country['country_id']] = country['country']
                return countries

            return {}
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}
