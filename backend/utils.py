import pandas as pd
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict

from core.order.models import Order


class CurrencyConversion:

    def __init__(self) -> None:
        self.url_course = 'https://www.cbr.ru/scripts/XML_daily.asp'
        self.currency_course = self._create_courses()

    def _create_courses(self) -> dict:
        response_xml = requests.get(self.url_course)
        tree = ET.ElementTree(ET.fromstring(response_xml.text))
        root = tree.getroot()

        currency_course = defaultdict(str)
        for child in root:
            values = [i.text for i in child]
            currency = values[1]
            course = float(values[-1].replace(',', '.'))
            currency_course[currency] = course

        return currency_course

    def convert_to_ruble(self, value, currency: str) -> float:
        value = float(value)
        course = self.currency_course[currency]
        result = value * course
        return result


class DFHandler:

    @staticmethod
    def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
        conversion = CurrencyConversion()
        df['price'] = df['price'].apply(conversion.convert_to_ruble, args=('USD',))
        df['price'] = pd.to_numeric(df['price'])
        df = df.astype({
            'id': 'int',
            'order_number': 'int',
        })
        df['delivery_expected'] = pd.to_datetime(
            df['delivery_expected'], format='%d.%m.%Y'
        ).dt.date

        return df

    @staticmethod
    def get_df_from_objects(objects: list[Order]) -> pd.DataFrame:
        columns = Order.__table__.columns.keys()

        data = list()
        for object in objects:
            row = object.get_values()
            data.append(row)

        df = pd.DataFrame(
            columns=columns,
            data=data
        )
        return df

    # Check df_1 if need update
    def df_need_update(
            self,
            df_1: pd.DataFrame, df_2: pd.DataFrame,
            idx_1: int, idx_2: int,
            column: str
        ) -> bool:
        column_values_equals = self.dfs_column_equals(df_1, df_2, idx_1, idx_2, column)
        row_values_equals = self.dfs_row_equals(df_1, df_2, idx_1, idx_2)

        if column_values_equals is False:
            return False
        if (column_values_equals is True) and \
           (row_values_equals is False):
            return True

        return False

    @staticmethod
    def dfs_column_equals(
            df_1: pd.DataFrame, df_2: pd.DataFrame,
            idx_1: int, idx_2: int,
            column: str
        ) -> bool:
        if df_1.at[idx_1, column] == df_2.at[idx_2, column]:
            return True
        else:
            return False

    @staticmethod
    def dfs_row_equals(
            df_1: pd.DataFrame, df_2: pd.DataFrame,
            idx_1: int, idx_2: int,
        ) -> bool:
        if all(df_1.loc[idx_1].values == df_2.loc[idx_2].values):
            return True
        else:
            return False
