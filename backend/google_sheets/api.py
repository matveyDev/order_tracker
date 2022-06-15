import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

from .settings import CREDENTIALS_FILE, \
                      SPREADSHEET_ID, \
                      SCOPES


class GoogleSheetsAPI:
    def __init__(self) -> None:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE,
            SCOPES
        )
        http_auth = credentials.authorize(httplib2.Http())
        self._service = apiclient.discovery.build(
            'sheets', 'v4',
            http=http_auth
        )

    def get_full_sheet(
            self,
            point_first: str, point_last: str,
            sheet_id: str = SPREADSHEET_ID,
            dimension: str = 'ROWS'
        ) -> dict:
        range = f'{point_first}:{point_last}'
        values = self._service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range,
            majorDimension=dimension
        ).execute()

        return values
