"""
Google sheets integration.
"""


from typing import List, Tuple

import gsheets

# Hardcoded credentials and storage path
# TODO: something better
_CREDENTIALS_PATH = "auth/google_credentials.json"
_STORAGE_PATH = "./sheets_storage.json"

# Hardcoded groceries spreadsheet URL
# TODO: something better
_SHEET_URL = "https://docs.google.com/spreadsheets/d/1dXAwYl6eVkqxiildHRyCgEzm8vgIQ0iKl79OgBwE134/edit#gid=827276232"  # noqa


def get_items(console) -> List[Tuple[str, int, str]]:
    session = gsheets.Sheets.from_files(_CREDENTIALS_PATH, _STORAGE_PATH)
    sheet = session.get(_SHEET_URL).first_sheet

    items = []
    row = 2

    while True:
        try:
            name = sheet.at(row=row, col=0)
            count = sheet.at(row=row, col=1)
        except IndexError:
            break

        try:
            description = sheet.at(row=row, col=2)
        except IndexError:
            description = ""

        item = (name, count, description)
        items.append(item)
        row += 1

    console.log(f"Loaded sheet: [yellow]{sheet.title}")

    return items
