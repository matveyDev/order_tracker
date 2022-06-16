import pandas as pd

from core.order.models import Order


class DFHandler:

    @staticmethod
    def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
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
