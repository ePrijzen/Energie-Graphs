import os
import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Credentials:
    def __init__(self) -> None:
        pass

    def check_credentials(self, credential_folder:str, credential_filename:str)->str:
        try:
            credential_file = os.path.join(credential_folder, credential_filename)
            if(self.check_credential_exists(credential_file=credential_file)):
                return credential_file
            return ""
        except Exception as e:
            log.critical(e, exc_info=True)
            return ""

    @staticmethod
    def check_credential_exists(credential_file:str = "")->bool:
        try:
            if not os.path.exists(credential_file):
                raise Exception(f"Config file not found : {credential_file}")
            return True
        except Exception as e:
            log.critical(e, exc_info=True)
            return False
