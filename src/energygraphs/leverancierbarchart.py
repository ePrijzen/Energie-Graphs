import os
import locale
import logging

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
matplotlib.use('Agg')

from energygraphs.graph import Graphs

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class LeverancierBarChart(Graphs):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def create_chart(self, data:dict, graph_file:str, title:str, subtitle:str, kind:str, avg_price:float, figsize:tuple=(11,7)):
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

            ax.margins(y=0.17, x=0.009)
            leveranciers = list(data.keys())
            prices = list(data.values())
            amount = len(leveranciers)

            ax.bar(leveranciers, prices, color=kind_color)
            # 'tab:blue'
            # ax.plot(ds["leverancier"], ds['TLV euro'], **{'color': line_color_1, 'marker': 'o'})
            if avg_price > 0:
                # plt.axhline(y=avg_price, **{'color': self.fixed_color})
                ax.axhline(y=avg_price, **{'color': self.fixed_color})

            bar_font_size = 8
            sum_rotation = 90
            if amount <= 21:
                sum_rotation = 0

            ax.bar_label(ax.containers[0], labels=[f'€ {x:n}' for x in ax.containers[0].datavalues], label_type="edge", rotation=sum_rotation,fontsize=bar_font_size)

            ax.yaxis.set_major_formatter(ticker.FuncFormatter(self.currency_format))

            ax.grid(axis='y', color='gainsboro')
            left = 0
            bottom = -0.15
            bottom_2 = -0.18

            sub_text = f"""{self.watermarksub}, leverancier prijzen zijn de variabele tarieven op basis van het instaptarief van een modelcontract.
Blauwe lijn is op basis van flex/inkoop all-in prijs (inkoop prijs+inkoopvergoeding+ODE+energiebelasting en BTW)"""

            ax.text(left, bottom_2, sub_text,
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

            ax.legend([ f"Gem. inkoop all-in prijs € {avg_price:n}", "Leverancierprijs"], bbox_to_anchor=(1, 1.2), loc='upper right', prop={'size': 8})

            fig.savefig(graph_file, bbox_inches='tight', dpi=200)
            ax.cla()
            fig.clf()
            plt.close('all')
            return True

        except (Exception, KeyError) as e:
            log.warning(e, exc_info=True)
            return False