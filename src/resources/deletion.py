import os
import logging
import shutil
from time import time

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class deletion:
    def __init__(self) -> None:
        pass

    def delete(self, path:str="", days:int=10)->bool:
        try:

            # converting days to seconds
            seconds = time() - (days * 24 * 60 * 60)

            # checking whether the file is present in path or not
            if os.path.exists(path):

                # iterating over each and every folder and file in the path
                for root_folder, folders, files in os.walk(path):
                    for folder in folders:
                        # folder path
                        folder_path = os.path.join(root_folder, folder)

                        # comparing with the days
                        if seconds >= self.get_file_or_folder_age(folder_path):
                            # invoking the remove_folder function
                            self.remove_folder(folder_path)

                    # checking the current directory files
                    for file in files:
                        # file path
                        file_path = os.path.join(root_folder, file)
                        # comparing the days
                        if seconds >= self.get_file_or_folder_age(file_path):
                            # invoking the remove_file function
                            self.remove_file(file_path)

                else:
                    # if the path is not a directory
                    # comparing with the days
                    if seconds >= self.get_file_or_folder_age(path):
                        # invoking the file
                        self.remove_file(path)
            else:
                # file/folder is not found
                log.error(f'"{path}" is not found')

            return True
        except Exception as e:
            log.critical(e, exc_info=True)
            return False

    @staticmethod
    def remove_folder(path):
        try:
            # removing the folder
            if not shutil.rmtree(path):
                return True

            raise Exception(f"Unable to delete {path}")

        except Exception as e:
            log.critical(e, exc_info=True)
            return False

    @staticmethod
    def remove_file(path):
        try:
            # removing the file
            if not os.remove(path):
                return True

            raise Exception(f"Unable to delete {path}")
        except Exception as e:
            log.critical(e, exc_info=True)
            return False

    @staticmethod
    def get_file_or_folder_age(path):
        try:
        # getting ctime of the file/folder
        # time will be in seconds
            ctime = os.stat(path).st_ctime
            return ctime
        except Exception as e:
            log.critical(e, exc_info=True)
            return False
