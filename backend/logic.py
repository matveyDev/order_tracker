import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, update, delete

from utils import DFHandler
from core.database.db import SQLALCHEMY_DATABASE_URL
from core.order.models import Order
from google_sheets.api import GoogleSheetsAPI


class OrderTrackBase:
    """
    Integration Postgres with GoogleSheets
    """
    def __init__(self) -> None:
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL)
        self.handler = DFHandler()

    def _get_df_from_sheet(self) -> pd.DataFrame:
        sheets_api = GoogleSheetsAPI()
        columns = Order.__table__.columns.keys()
        sheet = sheets_api.get_full_sheet(
            point_first='A',
            point_last='D'
        )['values'][1:]
        df_sheet = pd.DataFrame(
            columns=columns,
            data=sheet
        )
        df_sheet = self.handler.prepare_df(df_sheet)

        return df_sheet

    def _get_df_from_db(self) -> pd.DataFrame:
        session = Session(self.engine)
        objects = session.query(Order).all()
        df_db = self.handler.get_df_from_objects(objects)

        return df_db

    def _get_updated_df_db(
            self,
            df_db: pd.DataFrame,
            df_sheet: pd.DataFrame
        ) -> pd.DataFrame:
        df = df_db.copy()
        for idx_db in df.index:
            for idx_sheet in df_sheet.index:

                if self.handler.df_need_update(
                    df, df_sheet,
                    idx_db, idx_sheet,
                    'order_number'
                ):
                    df.loc[idx_db] = df_sheet.loc[idx_sheet]

        return df

    def _get_df_to_insert_in_db(
            self, df_db: pd.DataFrame, df_sheet:pd.DataFrame
        ) -> pd.DataFrame:
        df_sheet = df_sheet.copy()
        df_db = df_db.copy()

        for idx_sheet in df_sheet.index:
            for idx_db in df_db.index:
                if (idx_sheet in df_sheet.index) and \
                    self.handler.dfs_column_equals(
                    df_db, df_sheet, idx_db, idx_sheet, 'order_number'
                    ):
                    df_sheet = df_sheet.drop(idx_sheet)
                else:
                    continue

        return df_sheet

    @staticmethod
    def _get_orders_to_delete(df_db: pd.DataFrame, df_sheet: pd.DataFrame) -> list:
        order_numbers_to_delete = list()
        for _, row in df_db.iterrows():
            if row.order_number not in df_sheet.order_number.values:
                order_numbers_to_delete.append(row.order_number)

        return order_numbers_to_delete


class OrderTrackChecker(OrderTrackBase):

    @staticmethod
    def need_update_databse(df_1: pd.DataFrame, df_2: pd.DataFrame) -> bool:
        if not df_1.equals(df_2):
            return True
        else:
            return False

    @staticmethod
    def need_delete_from_db(df_db: pd.DataFrame, df_sheet: pd.DataFrame) -> bool:
        if len(df_db) > len(df_sheet):
            return True
        else:
            return False

    def need_insert_in_db(self, df_1: pd.DataFrame, df_2: pd.DataFrame):
        df_to_insert = self._get_df_to_insert_in_db(df_1, df_2)
        if not df_to_insert.empty:
            return True
        else:
            return False


class OrderTrack(OrderTrackBase):

    def __init__(self) -> None:
        super().__init__()
        self.checker = OrderTrackChecker()

        self.df_db = self._get_df_from_db()
        self.df_sheet = self._get_df_from_sheet()
        self.df_sheet.to_sql(
            'order_sheet', self.engine,
            if_exists='replace', index=False
        )

    def insert_in_db(self) -> bool:
        if self.checker.need_insert_in_db(self.df_db, self.df_sheet):
            df_to_insert = self._get_df_to_insert_in_db(self.df_db, self.df_sheet)
            df_to_insert.to_sql('order', self.engine, if_exists='append', index=False)
            
            return True
        else:
            return False

    def delete_from_db(self) -> bool:
        if self.checker.need_delete_from_db(self.df_db, self.df_sheet):
            df_sheet = self.df_sheet.sort_values('id')
            order_numbers = self._get_orders_to_delete(
                self.df_db, df_sheet
            )
            self._delete_from_db_by_order_number(order_numbers)

            return True
        else:
            return False

    def _delete_from_db_by_order_number(self, order_numbers: list) -> None:
        for order_number in order_numbers:
            # There are might be a better solution
            # Problem: Too many queries
            # ToDo: rewrite query
            query = (
                delete(Order).
                where(Order.order_number == order_number)
            )
            with self.engine.connect() as con:
                con.execute(query)

    def update_db(self) -> bool:
        updated_df_db = self._get_updated_df_db(
            self.df_db, self.df_sheet
        ).sort_values('id')

        if self.checker.need_update_databse(self.df_db, updated_df_db):
            df_db = self.df_db.sort_values('id')
            df_compared = updated_df_db.compare(
                df_db, keep_shape=True, keep_equal=True
            ).reset_index(drop=True)

            self._update_db_by_order_number(df_compared)

            return True
        else:
            return False

    def _update_db_by_order_number(self, df_compared: pd.DataFrame) -> None:
        columns = Order.__table__.columns.keys()
        columns.remove('id')

        for _, row in df_compared.iterrows():
            if not all([row[column].self == row[column].other for column in columns]):
                order_number = row.order_number.self
                query = (
                    update(Order).
                    where(Order.order_number == order_number).
                    values(
                        price=int(row.price.self),
                        delivery_expected=row.delivery_expected.self
                    )
                )
                with self.engine.connect() as con:
                    con.execute(query)
