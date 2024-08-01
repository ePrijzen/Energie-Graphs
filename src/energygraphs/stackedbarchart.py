import os
import locale
import numpy as np
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

class StackedBarChart(Graphs):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chart(self, data:dict, graph_file:str, title:str, subtitle:str, datekind:str="", kind:str="", verkoop:bool=False, belasting:dict={}, figsize:tuple=(11,7))->bool:
        try:

            match kind:
                case "g":
                    kind_color = self.gas_color
                case _:
                    kind_color = self.electric_color

            fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)

            ax.xaxis.set_label_position('top')
            ax.set_title(title, loc='left', weight='bold', fontsize=24, pad=15, color=kind_color)
            ax.set_xlabel(subtitle, loc='left', fontsize=16, labelpad=15)

            times = list(data.keys())
            price_data = list(data.values())
            prices = np.array(price_data)

            amount = len(times)

            p1 = ax.bar(range(len(times)), prices[:,0], color=kind_color)
            p2 = ax.bar(range(len(times)), prices[:,1], bottom=prices[:,0], color=self.fixed_color)

            # ax = plt.gca()

            if datekind is not None and datekind == "d":
                times = pd.to_datetime(times, format='%Y-%m-%d')
                plt.xticks(range(len(times)), times.strftime('%d %b %Y'))
            else:
                plt.xticks(range(len(times)), times)

            avg_total_prices = [pd[0]+pd[1] for pd in price_data]
            avg_purchase_prices = [pd[0] for pd in price_data]

            ax.axhline(y=np.nanmean(avg_total_prices), linestyle='--', linewidth=1, label='Gem. totaal prijs', color='red', alpha=0.50)
            ax.axhline(y=np.nanmean(avg_purchase_prices), linestyle='--', linewidth=1, label='Gem. inkoop prijs', color='green', alpha=0.50)

            sum_rotation = 90
            if amount <= 8:
                sum_rotation = 0

            for r1,r2 in zip(p1,p2):
                h1 = r1.get_height()
                h2 = r2.get_height()
                plt.text(r1.get_x()+r1.get_width()/2., h1+h2, ' € {:n}'.format(h1+h2), ha='center', va='bottom',  rotation=sum_rotation )

            for c in ax.containers:
                ax.bar_label(c, labels=[f'€ {a:n}' if a else "" for a in c.datavalues], label_type="center", color="white", rotation=sum_rotation)

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

            belasting_tekst = "Opslag + EnergieBelasting + BTW"
            if belasting is not None:
                belasting_tekst = f"Opslag (€ {belasting['opslag']:n}) + EnergieBelasting (€ {belasting['eb']:n}) + BTW ({belasting['btw']}%)"

            ax.legend([ 'Gem. totaal prijs', 'Gem. inkoop prijs', 'Inkoopprijs', belasting_tekst], bbox_to_anchor=(1, 1.2), loc='upper right', prop={'size': 8})
            ax.margins(y=0.17, x=0.009)

            fig.savefig(graph_file, bbox_inches='tight', dpi=200)
            ax.cla()
            fig.clf()
            plt.clf()
            plt.close('all')
            return True

        except (Exception, KeyError) as e:
            log.warning(e, exc_info=True)
            return False