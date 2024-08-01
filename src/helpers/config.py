import os
import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Config:
    def __init__(self) -> None:
        pass

    def check_config(self, config_folder:str, config_filename:str)->str:
        try:
            config_file = os.path.join(config_folder, config_filename)
            if(self.check_config_exists(config_file=config_file)):
                return config_file
            return ""
        except Exception as e:
            log.critical(e, exc_info=True)
            return ""

    @staticmethod
    def check_config_exists(config_file:str = "")->bool:
        try:
            if not os.path.exists(config_file):
                raise Exception(f"Config file not found : {config_file}")
            return True
        except Exception as e:
            log.critical(e, exc_info=True)
            return False
