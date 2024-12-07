"""
Использование декоратора
"""

import time
import json
import requests
from datetime import datetime
from xml.etree import ElementTree as ET


class BaseCurrenciesList():
    def get_currencies(self, currencies_ids_lst: list) -> dict:
        pass


class CurrenciesList(BaseCurrenciesList):
    def __init__(self):
        self.rates_available = False
        self.t = time.time() 
        self.dt = datetime.now().day 
        self.rates = None 

    def get_currencies(self, currencies_ids_lst: list = None) -> dict:
        t = time.time() 
        dt = datetime.today().day 

        result = {}
        
        if self.rates_available:
            return self.rates
        
        if not self.rates_available or (t - self.t > 3600 or dt != self.dt):
            if currencies_ids_lst is None:
                currencies_ids_lst = [
                    'R01239', 'R01235', 'R01035', 'R01815', 'R01585F', 'R01589',
                    'R01625', 'R01670', 'R01700J', 'R01710A'
                ]
            res = requests.get("http://www.cbr.ru/scripts/XML_daily.asp")
            cur_res_str = res.text

            root = ET.fromstring(cur_res_str)

            valutes = root.findall("Valute")

            for _v in valutes:
                valute_id = _v.get('ID')

                if str(valute_id) in currencies_ids_lst:
                    valute_cur_val = _v.find('Value').text
                    valute_cur_name = _v.find('Name').text

                    result[valute_id] = (valute_cur_val, valute_cur_name)

            self.rates = result
            self.rates_available = True

        return result


class Decorator(BaseCurrenciesList):
    """
    aka Decorator из примера паттерна
    """

    __wrapped_object: BaseCurrenciesList = None

    def __init__(self, currencies_lst: BaseCurrenciesList):
        self.__wrapped_object = currencies_lst

    @property
    def wrapped_object(self) -> str:
        return self.__wrapped_object

    def get_currencies(self, currencies_ids_lst: list = None) -> dict:
        return self.__wrapped_object.get_currencies(currencies_ids_lst)


class ConcreteDecoratorJSON(Decorator):
    def get_currencies(self, currencies_ids_lst: list = None) -> str:  
        return json.dumps(self.wrapped_object.get_currencies(currencies_ids_lst), ensure_ascii=False, indent=4)


class ConcreteDecoratorCSV(Decorator):
    def get_currencies(self, currencies_ids_lst: list = None) -> str:  
        currency_data = self.wrapped_object.get_currencies(currencies_ids_lst)

        if type(currency_data) is str:
            currency_data = json.loads(currency_data)
        
        csv_data = "ID;Rate;Name\n"
        for currency, val in currency_data.items():
            csv_data += f'{currency};{val[0]};{val[1]}\n'
        csv_data = csv_data.rstrip()
        return csv_data


def show_currencies(currencies: BaseCurrenciesList):
    """
       aka client_code() 
    """

    print(currencies.get_currencies())


if __name__ == "__main__":

    curlistdict = CurrenciesList() 
    wrappedcurlist = Decorator(curlistdict)
    wrappedcurlist_json = ConcreteDecoratorJSON(curlistdict)
    wrappedcurlist_csv = ConcreteDecoratorCSV(curlistdict)

    show_currencies(wrappedcurlist_json)
    show_currencies(wrappedcurlist_csv)
    show_currencies(wrappedcurlist)
