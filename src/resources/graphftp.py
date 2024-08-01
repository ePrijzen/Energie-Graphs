import os
import ftplib
import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class GraphFtp:
    def __init__(self, config:dict={}) -> None:
        try:
            if config is None:
                raise Exception('No config!')

            self.ip = config["ftp"]["ip"]
            self.user = config["ftp"]["user"]
            self.pwd = config["ftp"]["pwd"]

        except Exception as e:
            log.critical(e, exc_info=True)

    def upload(self, source:str="", target:str="")->bool:
        try:
            ftp = ftplib.FTP(self.ip, self.user, self.pwd)

            with open(source, "rb") as file:
                ftp.storbinary('STOR %s' % target, file)

            ftp.quit()
            # with ftplib.FTP_TLS(self.ip, self.user, self.pwd) as ftp:
            #     print(ftp.connect(self.ip, 21))
            #     print(ftp.login(self.user, self.pwd))
            #     print(ftp.getwelcome())
            #     print(ftp.set_debuglevel(2))
            #     print(ftp.prot_p())
            #     print(ftp.set_pasv(True))
            #     with open(source, "rb") as file:
            #         ftp.storbinary('STOR %s' % target, file)

            return True
        except Exception as e:
            log.critical(e, exc_info=True)
            return False
