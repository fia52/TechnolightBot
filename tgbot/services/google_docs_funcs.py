import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


class GoogleDocsRedactor:
    def __init__(self):
        credentials_file = "tgbot/services/creds.json"
        self.spreadsheet_id = "1bSTK2fuslI4iZPmIi4O7ZxgUZ5dlYiiEvpXF49qDFmI"
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file,
            [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        httpauth = credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build("sheets", "v4", http=httpauth)

    async def add_record_to_table(self, values: list, event_name: str):
        range = {
            "Кулинарный батл": "Лист1!A:D",
            "Большие гонки": "Лист1!F:I",
            "Битва умов": "Лист1!K:N",
            "Дневной дозор": "Лист1!P:S",
        }.get(event_name)

        result = (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=range,
                valueInputOption="USER_ENTERED",
                insertDataOption="OVERWRITE",
                body={"values": [values]},
            )
            .execute()
        )
