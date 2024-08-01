import os
import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Prices:

    @staticmethod
    def avg_data_per_country(data:dict={}, countries:dict={})->dict:
        try:
            if data is None or countries is None:
                raise Exception("geen data of landen")

            new_data_set = {}

            for d in data:
                country = countries[d['country']]
                new_data_set[country] = round(d['price'],3)
                pass

            return new_data_set
        except (Exception, KeyError) as e:
            log.warning(f"{e} | {d}", exc_info=True)
            return {}

    @staticmethod
    def process_prices(data:dict={}, dateortime:str="fromdate")->dict:
        try:
            inkoop_set = {}
            all_in_set = {}
            eb_set = {}
            eb_parts = {}

            for d in data:
                inkoop_set[d[dateortime]] = round(d['price'],3)
                all_in_set[d[dateortime]] = round(d['all_in_price'],3)
                eb_price = round(((d['all_in_price'])-d['price']),3)
                eb_set[d[dateortime]] = [round(d['price'],3), eb_price]
                vast = round((d['opslag']+d['ode']+d['eb']), 3)
                eb_parts[d[dateortime]] = [round(d['price'],3), vast, round(d['btw_total'],3)]

            return {'inkoop_set': inkoop_set, 'all_in_set':all_in_set,'eb_set':eb_set, "eb_parts": eb_parts}
        except (Exception, KeyError) as e:
            log.warning(f"{e} | {data}", exc_info=True)
            return {}

    @staticmethod
    def process_leveranciers(data:dict={})->dict:
        try:
            leveranciers = {}
            for d in data:
                leveranciers[d['leverancier']] = round(d['price'],3)
            return leveranciers
        except (Exception, KeyError) as e:
            log.warning(f"{e} | {data}", exc_info=True)
            return {}

    @staticmethod
    def dutch_floats(price:float = None,f:str=':.3f')->str:
        try:
            if price is None or price == "":
                return ""

            return ('€ {'+f+'}').format(price).replace('.',',')
        except (Exception, KeyError) as e:
            log.warning(e, exc_info=True)
            return ""
