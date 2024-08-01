import os
import locale
import logging

import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
matplotlib.use('Agg')

from energygraphs.graph import Graphs

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class BarChart(Graphs):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chart(self, data:dict, graph_file:str, subtitle:str, title:str, datekind:str=None, kind:str = None, verkoop:bool = False, belasting:dict=None, figsize:tuple=(11,7))->bool:
        try:
            fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
            # fig = figure.Figure(figsize=(11, 7), constrained_layout=True)
            # ax = fig.subplots(1)

            ax.xaxis.set_label_position('top')
            ax.set_title(title, loc='left', weight='bold', fontsize=24, pad=15)
            ax.set_xlabel(subtitle, loc='left', fontsize=16, labelpad=15)

            times = list(data.keys())
            prices = list(data.values())
            amount = len(times)
            min_price = min(prices)
            max_price = max(prices)
            avg = sum(v for k, v in data.items()) / len(data)

            # ax = plt.gca()

            profit_color = [{p<=min_price: '#79DE79', min_price<p<=avg: '#FCD060', p>avg: '#FB6962'}[True] for p in prices]

            if datekind is not None and datekind == "m":
                # ax.xaxis.set_major_formatter(mdates.DateFormatter('%B'))
                times = pd.to_datetime(times, format='%Y-%m-%d')
                ax.bar(times.strftime('%B'), prices, color=profit_color)
            elif datekind is not None and datekind == "d":
                times = pd.to_datetime(times, format='%Y-%m-%d')
                ax.bar(times.strftime('%d %b %Y'), prices, color=profit_color)
            else:
                ax.bar(times, prices, color=profit_color)

            sum_rotation = 90
            if amount <= 8:
                sum_rotation = 0

            ax.bar_label(ax.containers[0], labels=[f'€ {x:n}' for x in ax.containers[0].datavalues], label_type="edge", rotation=sum_rotation)

            ax.margins(y=0.17, x=0.009)

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

            fig.savefig(graph_file, bbox_inches='tight', dpi=200)
            ax.cla()
            fig.clf()
            plt.close('all')
            return True

        except (Exception, KeyError) as e:
            log.warning(e, exc_info=True)
            return False