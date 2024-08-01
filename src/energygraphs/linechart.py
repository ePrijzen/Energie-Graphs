import os
import locale
import logging

import pandas as pd

import matplotlib
# import matplotlib.pyplot as plt
from matplotlib import figure
import matplotlib.ticker as ticker
matplotlib.use('Agg')

from energygraphs.graph import Graphs

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class LineChart(Graphs):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chart(self, data:dict, graph_file:str, title:str, subtitle:str, datekind:str=None, kind:str=None, verkoop:bool=False, figsize:tuple=(11,7))->bool:
        try:

            match kind:
                case "g":
                    kind_color = self.gas_color
                case _:
                    kind_color = self.electric_color

            fig = figure.Figure(figsize=figsize, constrained_layout=True)
            ax = fig.subplots(1)

            ax.xaxis.set_label_position('top')
            ax.set_title(title, loc='left', weight='bold', fontsize=24, pad=15, color=kind_color)
            ax.set_xlabel(subtitle, loc='left', fontsize=16, labelpad=15)

            times = list(data.keys())
            prices = list(data.values())

            amount = len(times)

            if datekind is not None and datekind == "m":
                times = pd.to_datetime(times, format='%Y-%m-%d')
                ax.plot(times.strftime('%d %b %Y'), prices, **{'color': self.fixed_color, 'marker': 'o'})
                max_price = round((max(prices)*1.05),1)
                min_price = round(min(prices)*0.9,1)
            else:
                ax.plot(times, prices, **{'color': self.fixed_color, 'marker': 'o'})
                max_price = round((max(prices)*1.10),1)
                min_price = round(min(prices)*0.10,1)

            # ax.set_ylim(min_price, max_price)

            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.html
            ax.grid(axis='y', color='gray')
            ax.grid(axis='x', color='gainsboro')

            ax.yaxis.set_major_formatter(ticker.FuncFormatter(self.currency_format))

            left = 0
            bottom = -0.15
            bottom_2 = -0.18
            ax.text(left, bottom, self.watermarktext,
                    horizontalalignment='left',
                    verticalalignment='top',
                    transform=ax.transAxes, color="gray")

            if verkoop:
                subtext = f"{self.watermarksub}{self.watermarksub_2}"
            else:
                subtext = f"{self.watermarksub}."

            ax.text(left, bottom_2, subtext,
                    horizontalalignment='left',
                    verticalalignment='top',
                    fontsize="x-small",
                    transform=ax.transAxes, color="gray")

            ax.text(0.5, 0.5, 'EnergieAdviesZeeland', transform=ax.transAxes,
                    fontsize=40, color='gray', alpha=0.06,
                    ha='center', va='center', rotation=30)

            ax.tick_params(axis='y', colors='gray')
            ax.yaxis.get_label().set_fontsize(16)

            # Rotates and right-aligns the x labels so they don't crowd each other.
            for label in ax.get_xticklabels(which='major'):
                label.set(rotation=35, horizontalalignment='right')

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # fig.savefig(graph_file, bbox_inches='tight', width=0.4)
            fig.savefig(graph_file, bbox_inches='tight', dpi=200)
            ax.cla()
            fig.clear('all')
            fig.clf()

            return True

        except Exception as e:
            log.warning(e, exc_info=True)
            return False