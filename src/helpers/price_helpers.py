import os
import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class PriceHelpers():

    @staticmethod
    def avg_data(data:dict={}, countries:dict={})->dict:
        try:
            if data is None or countries is None:
                raise Exception("geen data of landen")

            new_data_set = {}

            for d in data:
                country = countries[d['country']]
                new_data_set[country] = d['price']
                pass

            return new_data_set
        except (Exception, KeyError) as e:
            log.warning(e, exc_info=True)
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

    @staticmethod
    def prijs_instelling_tekst(kind="k")->str:
        match kind:
            case 'k':
                return "Inkoop"
            case 'o':
                return "Inkoop+opslag+BTW "
            case 'a':
                return "All-In "
            case _:
                return "Inkoop"

    @staticmethod
    def prijs_kind(kind="k")->str:
        match kind:
            case 'k':
                return"price"
            case 'o':
                return"opslag_price"
            case 'a':
                return"all_in_price"
            case _:
                return"price"

    def get_prices(self, prices:dict)->dict:
        try:
            gas_price = ""
            el_price = ""
            gas_price_inkoop = ""
            el_price_inkoop = ""

            for p in prices['data']:
                if p['kind'] == 'g':
                    try:
                        gas_price = p['all_in_price']
                        gas_price_inkoop = p['price']
                    except Exception:
                        gas_price = ""
                        gas_price_inkoop = ""

                if p['kind'] == 'e':
                    try:
                        el_price = p['all_in_price']
                        el_price_inkoop = p['price']
                    except Exception:
                        el_price = ""
                        el_price_inkoop = ""

            return {'el_price_dutch' : self.dutch_floats(el_price),
                    'gas_price_dutch' : self.dutch_floats(gas_price),
                    'gas_inkoop_price_dutch' : self.dutch_floats(gas_price_inkoop),
                    'el_inkoop_price_dutch' : self.dutch_floats(el_price_inkoop),
                    'el_price': el_price,
                    'el_price_inkoop': el_price_inkoop
                    }

        except Exception as e:
            log.error(e, exc_info=True)
            return {}
