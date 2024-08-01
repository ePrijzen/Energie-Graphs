import sys
import os
import toml
import locale
from datetime import datetime, timedelta

import logging
import logging.config
from resources.belastingrequests import BelastingRequests
from resources.countryrequests import CountryRequests
from resources.deletion import deletion
from resources.generalrequests import GeneralRequests
from resources.generationrequests import GenerationsRequests
from resources.graphftp import GraphFtp
from resources.energierequests import EnergieRequests
from resources.prices import Prices
from resources.google_sheet import GoogleSheet
from resources.leverancierrequest import LeverancierRequests

from energygraphs.barchart import BarChart
from energygraphs.linechart import LineChart
from energygraphs.multilinechart import MultiLineChart
from energygraphs.multistackedbarchart import MultiStackedBarChart
from energygraphs.stackedbarchart import StackedBarChart
from energygraphs.leverancierbarchart import LeverancierBarChart
from energygraphs.avghorcountrybarchart import AvgHorCBarChart

from helpers.folder_setters import FolderSetters
from helpers.price_helpers import PriceHelpers
from helpers.config import Config
from helpers.credentials import Credentials
from helpers.dates_times import DatesTimes
from helpers.hashtags import HashTags


from apscheduler.schedulers.blocking import BlockingScheduler

locale.setlocale(locale.LC_NUMERIC, "nl_NL.UTF-8")
os.environ['TZ'] = 'Europe/Amsterdam'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PY_ENV = os.getenv('PY_ENV', 'dev')

if(FS := FolderSetters.setFolders(dir_path=DIR_PATH, py_env=PY_ENV)):
    logging.config.fileConfig(os.path.join(FS['config_folder'], 'logging.conf'))
    log = logging.getLogger(PY_ENV)
    logger = logging.getLogger()
    match PY_ENV:
        case 'dev':
            logger.setLevel(logging.INFO)
        case 'prod':
            logger.setLevel(logging.ERROR)
        case _:
            logger.setLevel(logging.INFO)
            pass
    GRAPHS_FOLDER = FS['graphs_folder']
else:
    sys.exit()

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

if (config_file := Config().check_config(config_filename=FS['config_filename'], config_folder=FS['config_folder'])):
    config = toml.load(config_file)
else:
    log.critical('cannot read config', exc_info=True)
    sys.exit()

try:
    if not (credential_file := Credentials().check_credentials(credential_folder=FS['config_folder'], credential_filename="credentials.json")):
        raise Exception('Google credential file not found')
except Exception as e:
    log.critical(e, exc_info=True)
    sys.exit()

class GraphsProcess():
    def __init__(self, config:dict, bearer_key:str) -> None:
        self.config = config
        self.bearer_key = bearer_key
        self.gFTP = GraphFtp(config=self.config)
        self.ER = EnergieRequests(config=self.config, bearer_key=self.bearer_key)
        self.graph_types = [{'figsize': (11,7), 'square': "", 'type': 'png'}, {'figsize': (11,11), 'square': "_square", 'type': 'jpg'}]
        pass

    def todays_belasting_kinds(self)->dict:
        try:
            Belr = BelastingRequests(config=self.config, bearer_key=self.bearer_key)
            if(todays_belasting := Belr.belasting(fromdate=DatesTimes.vandaag())):
                return Belr.split_belasting(belastingen=todays_belasting['data'])
            return {}
        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    def tomorrow_belasting_kinds(self)->dict:
        try:
            Belr = BelastingRequests(config=self.config, bearer_key=self.bearer_key)
            if(tomorrow_belasting := Belr.belasting(fromdate=DatesTimes.morgen())):
                return Belr.split_belasting(belastingen=tomorrow_belasting['data'])
            return {}
        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    def generation_today(self)->None:
        GR = GenerationsRequests(config=self.config, bearer_key=self.bearer_key)
        try:
            if(todays_generations := GR.generations_by_date(fromdate=DatesTimes.vandaag())):
                if(todays_generations := GR.split_generations(generations=todays_generations)):
                    for graph_type in self.graph_types:
                        title = "Wind- en Zonnevoorspelling"
                        subtitle = f"Verwachte opbrengsten zonnepanelen en windmolens\nop land en zee in MegaWatt {DatesTimes.leesbare_vandaag()}"
                        graph_name = f"wind_and_solar_forecast_vandaag{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        MultiLineChart().create_chart(data=todays_generations, graph_file=graph_file, title=title, subtitle=subtitle, figsize=graph_type['figsize'])

                        if PY_ENV == "prod" and os.path.exists(graph_file):
                            self.gFTP.upload(source=graph_file, target=graph_name)
            todays_generations = None
        except Exception as e:
            log.error(e, exc_info=True)

    def generation_tomorrow(self)->None:
        GR = GenerationsRequests(config=self.config, bearer_key=self.bearer_key)
        try:
            graph_file = ""
            graph_name = ""
            if(tomorrow_generations := GR.generations_by_date(fromdate=DatesTimes.morgen())):
                if(tomorrow_generations := GR.split_generations(generations=tomorrow_generations)):
                    for graph_type in self.graph_types:
                        title = "Wind- en Zonnevoorspelling"
                        subtitle = f"Verwachte opbrengsten zonnepanelen en windmolens\nop land en zee in MegaWatt {DatesTimes.leesbare_morgen()}"
                        graph_name = f"wind_and_solar_forecast_morgen{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        MultiLineChart().create_chart(data=tomorrow_generations, graph_file=graph_file, title=title, subtitle=subtitle, figsize=graph_type['figsize'])

                    if PY_ENV == "prod" and os.path.exists(graph_file):
                        self.gFTP.upload(source=graph_file, target=graph_name)
            tomorrow_generations = None
        except Exception as e:
            log.error(e, exc_info=True)

    def avg_e_price(self)->None:
        pass

    def Leveranciers(self)->None:
        try:
            avg_e_price = 0
            if(todays_data := self.ER.get_prices(datum=DatesTimes.vandaag(), kind="e", country="NL")):
                if(todays_prices := Prices.process_prices(data=todays_data['data'], dateortime="fromtime")):
                    avg_e_price = sum(todays_prices['all_in_set'].values()) / len(todays_prices['all_in_set'])

            if(LEV := LeverancierRequests(config=self.config, bearer_key=self.bearer_key)):
                if(LEV_raw_data := LEV.leveranciers(fromdate=DatesTimes.vandaag(), kind='e', country="NL")):
                    if(LEV_data := Prices.process_leveranciers(LEV_raw_data['data'])):
                        for graph_type in self.graph_types:
                            graph_name = f"electra_leverancier_barchart{graph_type['square']}.{graph_type['type']}"
                            graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                            lev_title = "Leveranciersprijzen Nederland"
                            subtitle = f"Stroom prijs per kWh - {DatesTimes.leesbare_vandaag()}"
                            LeverancierBarChart().create_chart(data=LEV_data, avg_price=avg_e_price, graph_file=graph_file, title=lev_title,
                                                                    subtitle=subtitle, kind='e', figsize=graph_type['figsize'])
                            if PY_ENV == "prod" and os.path.exists(graph_file):
                                self.gFTP.upload(source=graph_file, target=graph_name)

                avg_g_price = 0
                if(gas_data := self.ER.all_prices(fromdate=DatesTimes.vandaag(), fromtime="23:00", kind="g", country="NL")):
                    today_gas_price = Prices.process_prices(data=gas_data['data'], dateortime="fromdate")
                    avg_g_price = sum(today_gas_price['all_in_set'].values()) / len(today_gas_price['all_in_set'])

                if(LEV_raw_data := LEV.leveranciers(fromdate=DatesTimes.vandaag(), kind='g', country="NL")):
                    if(LEV_data := Prices.process_leveranciers(LEV_raw_data['data'])):
                        for graph_type in self.graph_types:
                            graph_name = f"gas_leverancier_barchart{graph_type['square']}.{graph_type['type']}"
                            graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                            lev_title = "Leveranciersprijzen Nederland"
                            subtitle = f"Gas prijs per m³ - {DatesTimes.leesbare_vandaag()}"
                            MM = LeverancierBarChart().create_chart(data=LEV_data, graph_file=graph_file, avg_price=avg_g_price, title=lev_title,
                                                                    subtitle=subtitle, kind='g', figsize=graph_type['figsize'])

                            if PY_ENV == "prod" and os.path.exists(graph_file):
                                self.gFTP.upload(source=graph_file, target=graph_name)

        except Exception as e:
            log.error(e, exc_info=True)

    def tomorrow_electra_graphs(self, kind="e", title="Stroomprijzen Nederland")->None:
        try:
            if DatesTimes.korte_tijd() >= 15:
                try:
                    if(tomorrow_e_data := self.ER.get_prices(datum=DatesTimes.morgen(), kind="e", country="NL")):
                        if(tomorrow_e_prices := Prices.process_prices(data=tomorrow_e_data['data'], dateortime="fromtime")):
                            for graph_type in self.graph_types:
                                graph_name = f"tomorrow_electra_daily_all_in_stacked_barchart{graph_type['square']}.{graph_type['type']}"
                                graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                                subtitle = f"All-in Prijs per uur/kWh - {DatesTimes.leesbare_morgen()}"
                                verkoop = True
                                MM = StackedBarChart().create_chart(data=tomorrow_e_prices['eb_set'], graph_file=graph_file,  title=title, subtitle=subtitle,
                                                                kind=kind, verkoop=verkoop, belasting=self.tomorrow_belasting_kinds()['e'], figsize=graph_type['figsize'])
                                if PY_ENV == "prod" and os.path.exists(graph_file):
                                    self.gFTP.upload(source=graph_file, target=graph_name)
                except Exception as e:
                    log.error(e, exc_info=True)
        except Exception as e:
            log.error(e, exc_info=True)


    def daily_electra_graphs(self, kind="e", title="Stroomprijzen Nederland")->None:
        try:
            if(todays_data := self.ER.get_prices(datum=DatesTimes.vandaag(), kind="e", country="NL")):
                if(todays_prices := Prices.process_prices(data=todays_data['data'], dateortime="fromtime")):

                    try:
                        for graph_type in self.graph_types:
                            graph_name = f"electra_inkoop_daily_barchart{graph_type['square']}.{graph_type['type']}"
                            graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                            subtitle = f"Inkoopprijs per kWh {DatesTimes.leesbare_vandaag()}"
                            verkoop = False
                            MM = BarChart().create_chart(data=todays_prices['inkoop_set'], graph_file=graph_file, title=title, subtitle=subtitle,
                                                        kind=kind, verkoop=verkoop, figsize=graph_type['figsize'])
                            if PY_ENV == "prod" and os.path.exists(graph_file):
                                self.gFTP.upload(source=graph_file, target=graph_name)
                    except Exception as e:
                        log.error(e, exc_info=True)

                    try:
                        for graph_type in self.graph_types:
                            graph_name = f"electra_daily_all_in_stacked_barchart{graph_type['square']}.{graph_type['type']}"
                            graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                            subtitle = f"All-in Prijs per uur/kWh - {DatesTimes.leesbare_vandaag()}"
                            verkoop = True
                            StackedBarChart().create_chart(data=todays_prices['eb_set'], graph_file=graph_file,  title=title, subtitle=subtitle,
                                                        kind=kind, verkoop=verkoop, belasting=self.todays_belasting_kinds()['e'], figsize=graph_type['figsize'])
                            if PY_ENV == "prod" and os.path.exists(graph_file):
                                self.gFTP.upload(source=graph_file, target=graph_name)

                        for graph_type in self.graph_types:
                            verkoop = True
                            graph_name = f"electra_daily_all_in_stacked_barchart_2{graph_type['square']}.{graph_type['type']}"
                            graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                            subtitle = f"All-in Prijs per uur/kWh - {DatesTimes.leesbare_vandaag()}"
                            MultiStackedBarChart().create_chart(data=todays_prices['eb_parts'], graph_file=graph_file, title=title, subtitle=subtitle,
                                                                kind=kind, verkoop=verkoop, belasting=self.todays_belasting_kinds()['e'], figsize=graph_type['figsize'])
                            if PY_ENV == "prod" and os.path.exists(graph_file):
                                self.gFTP.upload(source=graph_file, target=graph_name)
                    except Exception as e:
                        log.error(e, exc_info=True)

            todays_data = None
        except Exception as e:
            log.error(e, exc_info=True)

    def electra_history_graphs(self, title:str="Stroomprijzen Nederland", kind:str='e')->None:
        try:
            if(avg_e_prices_per_month_data := self.ER.avg_prices_per_month(fromdate=DatesTimes.eerste_dag_jaar(), todate=DatesTimes.last_day_of_prev_month(cur_date=DatesTimes.vandaag()) , kind="e", country="NL")):
                if(avg_e_prices_per_month_prices := Prices.process_prices(data=avg_e_prices_per_month_data['data'], dateortime="fromdate")):
                    for graph_type in self.graph_types:
                        graph_name = f"electra_avg_ytd_stacked_barchart{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        subtitle = f"Gemiddelde inkoopprijs per maand/kWh"
                        verkoop = False
                        BarChart().create_chart(data=avg_e_prices_per_month_prices['inkoop_set'], graph_file=graph_file,  title=title,
                                                     subtitle=subtitle, datekind="m", kind=kind, verkoop=verkoop, figsize=graph_type['figsize'])
                        if PY_ENV == "prod" and os.path.exists(graph_file):
                            self.gFTP.upload(source=graph_file, target=graph_name)

        except Exception as e:
            log.error(e, exc_info=True)

        try:
            if(avg_from_to_e_data := self.ER.avg_from_to_prices(fromdate=DatesTimes.datum_30_dagen_terug(), todate=DatesTimes.vandaag(), kind="e", country="NL")):
                if(avg_from_to_e_prices := Prices.process_prices(data=avg_from_to_e_data['data'], dateortime="fromdate")):
                    for graph_type in self.graph_types:
                        graph_name = f"electra_30_days_all_in_stacked_barchart{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        subtitle = "Gemiddelde All-In prijs per dag/kWh"
                        verkoop = True
                        StackedBarChart().create_chart(data=avg_from_to_e_prices['eb_set'], graph_file=graph_file, title=title, subtitle=subtitle,
                                                            datekind="d", kind=kind, verkoop=verkoop, belasting=self.todays_belasting_kinds()['e'], figsize=graph_type['figsize'])
                        if PY_ENV == "prod" and os.path.exists(graph_file):
                            self.gFTP.upload(source=graph_file, target=graph_name)
        except Exception as e:
            log.error(e, exc_info=True)

        try:
            if(power_data := self.ER.avg_from_to_prices(fromdate=DatesTimes.datum_14_dagen_terug(), todate=DatesTimes.morgen(), kind="e", country="NL", group_by='ft')):
                if(power_prices := Prices.process_prices(data=power_data['data'], dateortime="fromtime")):
                    graph_name = f"electra_15_days_hour_linechart{graph_type['square']}.{graph_type['type']}"
                    graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                    subtitle = "Gemiddelde inkoopprijs per Uur/kWh afgelopen 14 dagen"
                    verkoop = False
                    LineChart().create_chart(data=power_prices['inkoop_set'], graph_file=graph_file, title=title, subtitle=subtitle,
                                                  datekind="t", kind=kind, verkoop=verkoop, figsize=graph_type['figsize'])
                    if PY_ENV == "prod" and os.path.exists(graph_file):
                        self.gFTP.upload(source=graph_file, target=graph_name)
            power_data = None
            power_prices = None
        except Exception as e:
            log.error(e, exc_info=True)

    def gas_today_graphs(self, title:str="Gasprijzen Nederland", kind:str='g')->None:
        try:
            if(gas_data := self.ER.all_prices(fromdate=DatesTimes.week_geleden(), todate=DatesTimes.vandaag(), fromtime="23:00", kind="g", country="NL")):
                if(gas_prices := Prices.process_prices(data=gas_data['data'], dateortime="fromdate")):
                    for graph_type in self.graph_types:
                        graph_name = f"gas_7_days_inkoop_barchart{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        subtitle = "Inkoopprijs prijs per m³"
                        verkoop = False
                        MM = BarChart().create_chart(data=gas_prices['inkoop_set'], graph_file=graph_file, title=title, subtitle=subtitle,
                                                     datekind="d", kind=kind, verkoop=verkoop, figsize=graph_type['figsize'])

                        if PY_ENV == "prod" and os.path.exists(graph_file):
                            self.gFTP.upload(source=graph_file, target=graph_name)

                    for graph_type in self.graph_types:
                        graph_name = f"gas_7_days_all_in_barchart{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        subtitle = "Inkoopprijs per m³ inclusief opslag, energiebelasting en btw"
                        verkoop = True
                        MM = BarChart().create_chart(data=gas_prices['all_in_set'], graph_file=graph_file, title=title,
                                                     subtitle=subtitle, datekind="d", kind=kind, verkoop=verkoop,
                                                     belasting=self.todays_belasting_kinds()['g'], figsize=graph_type['figsize'])

                        if PY_ENV == "prod" and os.path.exists(graph_file):
                           self.gFTP.upload(source=graph_file, target=graph_name)

                    for graph_type in self.graph_types:
                        graph_name = f"gas_daily_all_in_stacked_barchart_2{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        subtitle = "Inkoopprijs per dag/m³, plus: \ninkoopvergoeding, energiebelasting en btw"
                        verkoop = True
                        MM = StackedBarChart().create_chart(data=gas_prices['eb_set'], graph_file=graph_file, title=title, subtitle=subtitle,
                                                        datekind="d", kind=kind, verkoop=verkoop, belasting=self.todays_belasting_kinds()['g'], figsize=graph_type['figsize'])

                        if PY_ENV == "prod" and os.path.exists(graph_file):
                            self.gFTP.upload(source=graph_file, target=graph_name)

                    for graph_type in self.graph_types:
                        graph_name = f"gas_daily_all_in_stacked_barchart{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        subtitle = "Inkoopprijs per dag/m³, plus: \ninkoopvergoeding, energiebelasting en btw"
                        MM = MultiStackedBarChart().create_chart(data=gas_prices['eb_parts'], graph_file=graph_file, title=title, subtitle=subtitle,
                                                        datekind="d", kind=kind, verkoop=verkoop, belasting=self.todays_belasting_kinds()['g'], figsize=graph_type['figsize'])

                        if PY_ENV == "prod" and os.path.exists(graph_file):
                            self.gFTP.upload(source=graph_file, target=graph_name)

        except Exception as e:
            log.error(e, exc_info=True)

    def gas_history_graphs(self, title:str="Gasprijzen Nederland", kind:str='g')->None:
        try:
            if(gas_data := self.ER.all_prices(fromdate=DatesTimes.datum_15_dagen_terug(), todate=DatesTimes.morgen(), fromtime="23:00", kind="g", country="NL")):
                if(gas_prices := Prices.process_prices(data=gas_data['data'], dateortime="fromdate")):
                    for graph_type in self.graph_types:
                        graph_name = f"gas_15_days_all_in_linechart{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        subtitle = "Inkoopprijs per m³ inclusief opslag, energiebelasting en btw"
                        verkoop = True
                        MM = LineChart().create_chart(data=gas_prices['all_in_set'], graph_file=graph_file, title=title, subtitle=subtitle,
                                                    datekind="m", kind=kind, verkoop=verkoop, figsize=graph_type['figsize'])
                        if PY_ENV == "prod" and os.path.exists(graph_file):
                            self.gFTP.upload(source=graph_file, target=graph_name)
        except Exception as e:
            log.error(e, exc_info=True)

        try:
            if(gas_data := self.ER.all_prices(fromdate=DatesTimes.datum_30_dagen_terug(), todate=DatesTimes.vandaag(), fromtime="23:00", kind="g", country="NL")):
                if(gas_prices := Prices.process_prices(data=gas_data['data'], dateortime="fromdate")):
                    for graph_type in self.graph_types:
                        graph_name = f"gas_30_days_all_in_stacked_barchart{graph_type['square']}.{graph_type['type']}"
                        graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                        subtitle = "All-In prijs per dag/m³"
                        verkoop = True
                        MM = StackedBarChart().create_chart(data=gas_prices['eb_set'], graph_file=graph_file, title=title, subtitle=subtitle, datekind="d",
                                                        kind=kind, verkoop=verkoop, belasting=self.todays_belasting_kinds()['g'], figsize=graph_type['figsize'])
                        if PY_ENV == "prod" and os.path.exists(graph_file):
                            self.gFTP.upload(source=graph_file, target=graph_name)
        except Exception as e:
            log.error(e, exc_info=True)


    def country_graphs(self)->None:
        try:
            self.CR = CountryRequests(config=self.config, bearer_key=self.bearer_key)
            if(countries := self.CR.countries_api_call()):
                if(avg_country_data := self.ER.avg_prices(datum=DatesTimes.vandaag(), kind="e")):
                    if(avg_country_prices := Prices.avg_data_per_country(data=avg_country_data['data'],countries=countries)):
                        for graph_type in self.graph_types:
                            graph_name = f"electra_avg_day_price_countries_barchart{graph_type['square']}.{graph_type['type']}"
                            graph_file = os.path.join(FolderSetters.vandaag_path(graphs_folder=GRAPHS_FOLDER), graph_name)
                            sep_title = "Stroomprijzen Europa"
                            subtitle = f"Gemiddelde inkoopprijs per kWh/land - {DatesTimes.leesbare_vandaag()}"
                            verkoop = False
                            MM = AvgHorCBarChart().create_chart(data=avg_country_prices, graph_file=graph_file, countries=countries,
                                                                title=sep_title, subtitle=subtitle, verkoop=verkoop, figsize=graph_type['figsize'])
                            if PY_ENV == "prod" and os.path.exists(graph_file):
                                self.gFTP.upload(source=graph_file, target=graph_name)
        except Exception as e:
            log.error(e, exc_info=True)

def bearer_key()->str:
    try:
        GR = GeneralRequests(config=config)
        if not (password := GR.get_password(password=config["api"]["password"], salt=config["api"]["salt"])):
            raise Exception('No password!!')
        if(bearer_key := GR.get_bearer_key(email=config['api']['email'] ,password=password)):
            return bearer_key
        else:
            raise Exception('No bearer key!!')
    except (Exception, KeyError) as e:
        log.critical(e, exc_info=True)
        return ''

def delete_old_shit()->None:
    deletion().delete(path=GRAPHS_FOLDER,days=30)

def zon_wind_vandaag()->None:
    gp = GraphsProcess(config=config, bearer_key=bearer_key())
    gp.generation_today()
    pass

def zon_wind_morgen()->None:
    gp = GraphsProcess(config=config, bearer_key=bearer_key())
    gp.generation_tomorrow()
    pass

def electra_today_graphs()->None:
    gp = GraphsProcess(config=config, bearer_key=bearer_key())
    gp.daily_electra_graphs()

def electra_tomorrow_graphs()->None:
    gp = GraphsProcess(config=config, bearer_key=bearer_key())
    gp.tomorrow_electra_graphs()

def power_history_graphs()->None:
    gp = GraphsProcess(config=config, bearer_key=bearer_key())
    gp.electra_history_graphs()

def gas_today_graphs()->None:
    gp = GraphsProcess(config=config, bearer_key=bearer_key())
    gp.gas_today_graphs()

def gas_history_graphs()->None:
    gp = GraphsProcess(config=config, bearer_key=bearer_key())
    gp.gas_history_graphs()

def country_graphs()->None:
    gp = GraphsProcess(config=config, bearer_key=bearer_key())
    gp.country_graphs()

def leveranciers()->None:
    gp = GraphsProcess(config=config, bearer_key=bearer_key())
    gp.Leveranciers()

def proces_graphs()->None:
    delete_old_shit()
    gas_history_graphs()
    power_history_graphs()
    zon_wind_vandaag()
    country_graphs()
    electra_today_graphs()
    gas_today_graphs()
    leveranciers()
    electra_tomorrow_graphs()
    zon_wind_morgen()


if __name__ == "__main__":
    try:
        logging.error("Script started.")
        sys.excepthook = handle_exception
        # verwerk direct bij opstart op dev
        proces_graphs()

        if PY_ENV == 'prod':
        # daarna start interval
            scheduler = BlockingScheduler()
            scheduler.add_job(delete_old_shit, trigger='cron', hour='1', minute='1', timezone='Europe/Amsterdam')

            scheduler.add_job(gas_history_graphs, trigger='cron', hour='1,5', minute='5', timezone='Europe/Amsterdam')
            scheduler.add_job(power_history_graphs, trigger='cron', hour='1,5', minute='10', timezone='Europe/Amsterdam')
            scheduler.add_job(zon_wind_vandaag, trigger='cron', hour='1,5', minute='15', timezone='Europe/Amsterdam')
            scheduler.add_job(country_graphs, trigger='cron', hour='1,5', minute='20', timezone='Europe/Amsterdam')

            scheduler.add_job(electra_today_graphs, trigger='cron', hour='1,6', minute='30', timezone='Europe/Amsterdam')
            scheduler.add_job(gas_today_graphs, trigger='cron', hour='1,6', minute='40', timezone='Europe/Amsterdam')

            scheduler.add_job(leveranciers, trigger='cron', day='1,10,20,30', hour='23', minute='10', timezone='Europe/Amsterdam')

            scheduler.add_job(electra_tomorrow_graphs, trigger='cron', hour='16', minute='5', timezone='Europe/Amsterdam')
            scheduler.add_job(zon_wind_morgen, trigger='cron', hour='16', minute='25', timezone='Europe/Amsterdam')

            scheduler.start()
    except (Exception, KeyError) as e:
        log.critical(e, exc_info=True)
