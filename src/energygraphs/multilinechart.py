import os
import locale
import logging
import matplotlib
from matplotlib import figure
matplotlib.use("Agg")

from energygraphs.graph import Graphs

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class MultiLineChart(Graphs):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chart(self, data:dict, graph_file:str, title:str, subtitle:str, figsize:tuple=(11,7))->bool:
        try:
            kind_color = self.electric_color

            fig = figure.Figure(figsize=figsize, constrained_layout=True)
            ax = fig.subplots(1)

            ax.xaxis.set_label_position('top')
            ax.set_title(title, loc='left', weight='bold', fontsize=24, pad=15, color=kind_color)
            ax.set_xlabel(subtitle, loc='left', fontsize=16, labelpad=15)

            data_part = data['solar']
            times = list(data_part.keys())
            mw = list(data_part.values())

            ax.plot(times, mw, **{'color': self.solar_color, 'marker': 'o'})

            data_part = data['w_on']
            times = list(data_part.keys())
            mw = list(data_part.values())
            ax.plot(times, mw, **{'color': self.land_color, 'marker': 'o'})

            data_part = data['w_off']
            times = list(data_part.keys())
            mw = list(data_part.values())
            ax.plot(times, mw, **{'color': self.sea_color, 'marker': 'o'})

            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.html
            ax.grid(axis='y', color='gray')
            ax.grid(axis='x', color='gainsboro')

            left = 0
            bottom = -0.15
            bottom_2 = -0.18
            ax.text(left, bottom, self.watermarktext,
                    horizontalalignment='left',
                    verticalalignment='top',
                    transform=ax.transAxes, color="gray")

            subtext = f"{self.watermarksub}."

            ax.text(0.5, 0.5, 'EnergieAdviesZeeland', transform=ax.transAxes,
                    fontsize=40, color='gray', alpha=0.06,
                    ha='center', va='center', rotation=30)

            ax.text(left, bottom_2, subtext,
                    horizontalalignment='left',
                    verticalalignment='top',
                    fontsize="x-small",
                    transform=ax.transAxes, color="gray")

            ax.tick_params(axis='y', colors='gray')
            ax.yaxis.get_label().set_fontsize(16)

            # Rotates and right-aligns the x labels so they don't crowd each other.
            for label in ax.get_xticklabels(which='major'):
                label.set(rotation=35, horizontalalignment='right')

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            ax.legend([ 'Zonne-energie', 'Wind-energie land', 'Wind-energie zee'], bbox_to_anchor=(1, 1.2), loc='upper right')

            fig.savefig(graph_file, bbox_inches='tight', dpi=200)

            ax.cla()
            fig.clear('all')
            fig.clf()
            return True

        except Exception as e:
            log.warning(e, exc_info=True)
            return False