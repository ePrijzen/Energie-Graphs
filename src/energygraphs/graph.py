import os
import locale
import requests

import matplotlib
import matplotlib.pyplot as plt
# from matplotlib import plt
matplotlib.use('Agg')

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from io import BytesIO

import logging

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Graphs(object):

    def __init__(self)->None:
        self.watermarktext = "Aangeboden door: energieadvieszeeland.nl"
        self.watermarksub = "Aan dit overzicht kunnen geen rechten ontleend worden"

        self.watermarksub_2 = ", totaalprijs is verkoopprijs bij energieleveranciers met flexibele energiecontracten."
        self.watermarksub_3 = "."

        self.electric_color = "#CA7A23"
        self.gas_color = "#1E9A2A"

        self.fixed_color = "#384C6B"
        self.var_color = "#859BBA"

        self.sea_color = "#67C1CA"
        self.land_color = "#BC9354"
        self.solar_color = "#FFCF63"
        pass

    @staticmethod
    def currency_format(x, p):
        f=':.2f'
        return ('€ {'+f+'}').format(x).replace('.',',')


    @staticmethod
    def offset_image(x:str=None, y:str=None, flag:str=None, bar_is_too_short:int=None, ax:object=None):
        try:
            match flag:
                case "dk_1":
                    flag = "dk"
                case "de_lu":
                    flag = "de"
                case "no_1":
                    flag = "no"
                case "no_2":
                    flag = "no"
                case "se_3":
                    flag = "se"
                case "ie_sem":
                    flag = "ie"
                case "it_nord":
                    flag = "it"
                case _:
                    pass

            response = requests.get(f"https://flagcdn.com/w20/{flag}.png")
            img = plt.imread(BytesIO(response.content))
            im = OffsetImage(img, zoom=0.65)
            im.image.axes = ax
            x_offset = -50
            if bar_is_too_short:
                x = 0.05
            ab = AnnotationBbox(im, (x, y), xybox=(x_offset, 0), frameon=False,
                                xycoords='data', boxcoords="offset points", pad=0)
            ax.add_artist(ab)
        except Exception as e:
            log.warning(e, exc_info=True)
            return False

    @staticmethod
    def get_key(val:str=None, my_dict:dict=None):
        try:
            for key, value in my_dict.items():
                if val == value:
                    return key

            return False
        except Exception as e:
            log.warning(e, exc_info=True)
            return False

    @staticmethod
    def currency_format(x, p):
        f=':.2f'
        return ('€ {'+f+'}').format(x).replace('.',',')