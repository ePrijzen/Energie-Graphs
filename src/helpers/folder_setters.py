import os
import logging
from helpers.dates_times import DatesTimes

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class FolderSetters:
    @staticmethod
    def setFolders(dir_path:str, py_env:str):
        try:
            fs = {}
            match py_env:
                case 'dev':
                    fs['config_filename'] = "development.toml"
                    fs['config_folder'] = os.path.join(dir_path, "..","config")
                    fs['log_folder'] = os.path.join(dir_path, "..", "logging")
                    fs['graphs_folder'] = os.path.join(dir_path, "..", "..", "graphs")
                case 'prod':
                    fs['config_filename'] = "production.toml"
                    fs['config_folder'] = os.path.join(dir_path, 'config')
                    fs['log_folder'] = os.path.join(dir_path, "logging")
                    fs['graphs_folder'] = os.path.join(dir_path, "graphs")
                case _:
                    pass

            os.makedirs(fs['log_folder'], exist_ok=True)

            return fs
        except Exception as e:
            return False

    @staticmethod
    def vandaag_path(graphs_folder:str)->str:
        try:
            vandaag_path = os.path.join(graphs_folder, DatesTimes.vandaag_dir())
            os.makedirs(vandaag_path, exist_ok=True)
            return vandaag_path
        except (Exception, KeyError) as e:
            log.critical(e, exc_info=True)
            return ""
