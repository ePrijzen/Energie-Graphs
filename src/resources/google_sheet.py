# https://pyshark.com/google-sheets-api-using-python/
import os
import gspread
import pandas as pd
import logging
# from gspread_dataframe import set_with_dataframe
# from oauth2client.service_account import ServiceAccountCredentials

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class GoogleSheet:
    def __init__(self, config:dict={}, credential_file:str ="") -> None:
        try:
            self.gc = gspread.service_account(filename=credential_file)
            self.gsheet = self.gc.open_by_url(config["google"]["sheeturl"])
        except Exception as e:
            log.error(e, exc_info=True)
        pass

# edit
    def fill_sheet(self, data:dict={}, sheet:str = "")->None:
        try:
            ws = self.gsheet.worksheet(sheet)
            ws.clear()
            data_list = []
            data_list.append(['fromdate', 'fromtime', 'kind', 'country', 'price', 'opslag_price', 'all_in_price'])
            for d in data:
                data_list.append([*d.values()])
            ws.append_rows(data_list)
        except Exception as e:
            log.error(e, exc_info=True)
