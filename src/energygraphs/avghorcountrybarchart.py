import os
import random
import locale
import numpy as np
import logging

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
matplotlib.use('Agg')

from energygraphs.graph import Graphs

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class AvgHorCBarChart(Graphs):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chart(self, data:dict, graph_file:str, countries:dict, title:str, subtitle:str, verkoop:bool=False, figsize:tuple=(11,7))->bool:
        try:

            fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
            # fig = figure.Figure(figsize=(11, 7), constrained_layout=True)
            # ax = fig.subplots(1)

            ax.xaxis.set_label_position('top')
            ax.set_title(title, loc='left', weight='bold', fontsize=24, pad=15)
            ax.set_xlabel(subtitle, loc='left', fontsize=16, labelpad=15)

            colors = ["#FE8000", "#EFBD76", "#FFA52B", "#FF9D3C", "#FFF858", "#FCFFCB", "#07EEB2", "#FF4179","#E05B4B", "#E09336", "#DAB552", "#DBD9A6", "#87B49C", "#4B8A7E", "#A5DD96", "#E1F3C9", "#0095AD", "#00D5E5", "#82E9F0", "#C0ED42", "#FFE301", "#FFF352", "#FF85DA", "#FF69B3","#A15AC4", "#3F7539", "#B8CBAD", "#E1E2C2", "#F84040", "#9D1E29"]
            random.shuffle(colors)

            values = 2 ** np.random.randint(2, 10, len(data))
            max_value = values.max()

            labels = list(data.keys())
            values = list(data.values())

            height = 0.9
            ax.barh(y=labels, width=values, height=height, color=colors, align='center', alpha=0.8)

            # ax = plt.gca()
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.currency_format))

            # ax.bar_label(ax.containers[0], labels=[f'€ {x:n}' for x in ax.containers[0].datavalues], label_type="edge", padding=-50)
            ax.bar_label(ax.containers[0], labels=[f'€ {x:n}' for x in ax.containers[0].datavalues], label_type="edge", padding=5)

            left = 0
            bottom = -0.05
            bottom_2 = -0.08
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

            for i, (label, value) in enumerate(zip(labels, values)):
                if(country_iso := self.get_key(val=label, my_dict=countries).lower()):
                    self.offset_image(x=value, y=i, flag=country_iso, bar_is_too_short=value < max_value / 10, ax=ax)

            ax.set_yticks(labels)
            ax.set_yticklabels(labels)

            for lab in ax.get_yticklabels():
                if lab.get_text() == "Nederland":
                    lab.set_fontweight('bold')

            # plt.subplots_adjust(left=0.15)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            ax.margins(y=0.009)

            fig.savefig(graph_file, bbox_inches='tight', dpi=200)
            ax.cla()
            fig.clf()
            plt.close('all')
            return True

        except (Exception, KeyError) as e:
            log.warning(e, exc_info=True)
            return False