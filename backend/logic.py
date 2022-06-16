import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from utils import Handler
from core.database.db import SQLALCHEMY_DATABASE_URL
from core.order.models import Order
from google_sheets.api import GoogleSheetsAPI


# ToDo: Separate on 2 classes
class OrderTracker:
    """
    Integration Postgres with GoogleSheets
    """
    def __init__(self) -> None:
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL)
        self.sheets_api = GoogleSheetsAPI()
        self.handler = Handler()

    def _get_df_from_sheet(self) -> pd.DataFrame:
        columns = Order.__table__.columns.keys()
        sheet = self.sheets_api.get_full_sheet(
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

                if self.handler.need_update(
                    df, df_sheet,
                    idx_db, idx_sheet,
                    'order_number'
                ):
                    df.loc[idx_db] = df_sheet.loc[idx_sheet]
                else:
                    pass
        
        return df

    def check_and_update_database(self) -> bool:
        df_sheet = self._get_df_from_sheet()
        df_db = self._get_df_from_db()
        updated_df_db = self._get_updated_df_db(df_db, df_sheet)
        
        if not df_db.equals(updated_df_db):
            # Update DataBase here
            return True
        else:
            return False
