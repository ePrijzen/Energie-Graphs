
import os
import logging
from datetime import datetime, timedelta

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class DatesTimes:
    def __init__(self) -> None:
        self.weekdays = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']
        self.months = ['', 'Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Juni', 'Juli', 'Aug', 'Sept', 'Okt', 'Nog', 'Dec']

        self.morgen_tijden = list(['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00'])
        self.middag_tijden = list(['12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'])

    @staticmethod
    def last_day_of_prev_month(cur_date):
        try:
            format_str = '%Y-%m-%d'
            datetime_obj = datetime.strptime(cur_date, format_str)
            first_day_of_this_month = datetime_obj.replace(day=1)
            last_day_of_prev_month = first_day_of_this_month - timedelta(days=1)
            return last_day_of_prev_month.strftime("%Y-%m-%d")
        except (Exception, KeyError) as e:
            log.critical(e, exc_info=True)

    @staticmethod
    def datum_15_dagen_terug()->str:
        vandaag_ts = datetime.now()
        laatste_15_dagen_tf = vandaag_ts + timedelta(days=-15)
        return laatste_15_dagen_tf.strftime("%Y-%m-%d")

    @staticmethod
    def leesbare_morgen()->str:
        vandaag_ts = datetime.now()
        morgen_strf = vandaag_ts + timedelta(days=+1)
        return morgen_strf.strftime("%d %B %Y")

    @staticmethod
    def datum_30_dagen_terug()->str:
        vandaag_ts = datetime.now()
        laatste_30_dagen_tf = vandaag_ts + timedelta(days=-30)
        return laatste_30_dagen_tf.strftime("%Y-%m-%d")

    @staticmethod
    def vandaag()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%Y-%m-%d")

    @staticmethod
    def morgen()->str:
        vandaag_ts = datetime.now()
        morgen_ts = vandaag_ts + timedelta(days=+1)
        return morgen_ts.strftime("%Y-%m-%d")

    @staticmethod
    def vandaag_dir()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%Y%m%d")

    @staticmethod
    def maand()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%m")

    @staticmethod
    def datum_14_dagen_terug()->str:
        vandaag_ts = datetime.now()
        laatste_14_dagen_tf = vandaag_ts + timedelta(days=-14)
        return laatste_14_dagen_tf.strftime("%Y-%m-%d")

    @staticmethod
    def week_geleden()->str:
        vandaag_ts = datetime.now()
        week_geleden_strf = vandaag_ts + timedelta(days=-7)
        return week_geleden_strf.strftime("%Y-%m-%d")

    @staticmethod
    def jaarmaand()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%Y-%m")

    def maand_naam(self, maand:int=0)->str:
        if maand == 0 or maand is None:
            maand = int(self.maand())
        return self.months[maand]

    @staticmethod
    def jaar()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%Y")

    @staticmethod
    def dag()->int:
        vandaag_ts = datetime.now()
        return int(vandaag_ts.strftime("%d"))

    @staticmethod
    def eerste_dag_jaar()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%Y-01-01")

    @staticmethod
    def leesbare_vandaag()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%d %B")

    @staticmethod
    def tijd()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%H:00")

    @staticmethod
    def korte_tijd()->int:
        vandaag_ts = datetime.now()
        return int(vandaag_ts.strftime("%H"))

    @staticmethod
    def kort_dag()->int:
        vandaag_ts = datetime.now()
        return int(vandaag_ts.strftime("%d"))

    def day_part(start:int, hours:int)->list:
        try:
            stop = start+hours
            if ((stop-start) % 2) != 0:
                stop += 1
            if (stop > 24):
                start -= 1
                stop = 24

            part = []
            chunked_list = list()
            for i in range(start, stop):
                if i is not None:
                    if i == 24:
                        i = 0
                    part.append(f"{i:02d}:00")

            chunk_size = int(len(part)/2)
            for i in range(0, len(part), chunk_size):
                chunked_list.append(part [i:i+chunk_size])
            return chunked_list
        except Exception as e:
            log.error(e, exc_info=True)
            return []

    @staticmethod
    def next_hour(hour:str= "")->str:
        try:
            if hour is None:
                raise Exception('Geen uur mee gegeven')
            next_hour = int(hour[:2]) + 1
            return f"{next_hour:02d}:00"
        except Exception as e:
            log.error(e, exc_info=True)
            return ""

    def get_nice_day(self, date:str = "", weekday:bool = False) -> str:
        try:
            if date is None:
                vandaag_ts = datetime.now()
                date = vandaag_ts.strftime("%Y-%m-%d")

            date = f"{date} 01:01:01"
            dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

            day = dt.strftime("%d")
            year = dt.strftime("%Y")
            weekday = self.weekdays[dt.weekday()]
            month_int = int(dt.strftime("%m"))
            month = self.months[month_int]

            if weekday:
                return f"{weekday} {day} {month} {year}"
            else:
                return f"{day} {month} {year}"

        except Exception as e:
            log.error(e, exc_info=True)
            return ""
