import pickle, os.path, datetime
from sopel.module import commands, thread, require_privmsg, require_chanmsg
from googleapiclient.discovery import build
from google.oauth2 import service_account as s_a

SECRET = os.path.join(os.getcwd(), ".sopel/modules/smiley-sopel-secret.json")
SCOPES = ['https://www.googleapis.com/auth/drive']

def new_blank_sheet(bot, NUM_PLAYERS):
    c = s_a.Credentials.from_service_account_file(SECRET, scopes=SCOPES)
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    service = build('sheets', 'v4', credentials=c)
    drive_service = build('drive', 'v3', credentials=c)

    # Call the Sheets API
    bot.memory["sheet"] = service.spreadsheets()
    
    # Create a spreadsheet
    now = datetime.datetime.now()
    todays_date = now.strftime("%b %d, %Y")
    title = "Pact Dice Draft " + todays_date
    spreadsheet = {"properties": {"title": title}}
    spreadsheet = bot.memory["sheet"].create(body = spreadsheet, fields="spreadsheetId").execute()
    
    # Get the ID
    ID = spreadsheet.get("spreadsheetId")

    # Give public permissions
    view = {"type":"anyone","role":"reader"}
    perm_result = drive_service.permissions().create(fileId=ID,body=view).execute()
    
    # Write draft table
    # Write column headers
    column_headers = [""] + list(range(1,NUM_PLAYERS + 1))
    values = [column_headers]
    body = {"values": values}
    write_res = bot.memory["sheet"].values().update(spreadsheetId=ID,range="A1",valueInputOption="RAW",body=body).execute()
    # Write row headers
    row_headers = ["","Puissance","Longevity","Access",
                    "Executions","Research","Schools",
                    "Priority","Family"]
    values = [row_headers]
    body = {"values": values, "majorDimension":"COLUMNS"}
    write_res = bot.memory["sheet"].values().update(spreadsheetId=ID,range="A1",valueInputOption="RAW",body=body).execute()
    
    # Write karma table
    column_headers = ["", "White","Black"]
    body = {"values": [column_headers]}
    write_res = bot.memory["sheet"].values().update(spreadsheetId=ID,range="A11",valueInputOption="RAW",body=body).execute()
    
    # Formatting borders
    range_ = {"sheetId":0,"startRowIndex":0,"endRowIndex":12+NUM_PLAYERS,
                "startColumnIndex":0,"endColumnIndex":NUM_PLAYERS+1}
    white = {"blue":1,"red":1,"green":1}
    white_solid = {"style": "SOLID", "color": white}
    update_borders = {"range":range_,"top":white_solid,"left":white_solid,
                    "right":white_solid,"bottom":white_solid,"innerVertical":white_solid,
                    "innerHorizontal":white_solid}
    requests = [{"updateBorders": update_borders}]
    
    # Trim rows
    delete_rows = {"range": {"sheetId":0,"dimension":"ROWS","startIndex":11+NUM_PLAYERS}}
    requests.append({"deleteDimension": delete_rows})

    # Trim columns
    delete_cols = {"range": {"sheetId":0,"dimension":"COLUMNS","startIndex":NUM_PLAYERS+1}}
    requests.append({"deleteDimension": delete_cols})

    # Format cells (broad)
    blackish = {"red":0.15,"blue":0.15,"green":0.15}
    cell = {"userEnteredFormat":{"backgroundColor":blackish,
                                "textFormat":{"foregroundColor":white,
                                                "fontFamily": "Cabin",
                                                "fontSize":12,
                                                "bold":True}}}
    repeat_cell = {"range":range_, "cell": cell, "fields":"userEnteredFormat(backgroundColor,textFormat)"}
    requests.append({"repeatCell": repeat_cell})
    
    # Paint background gray
    gray_val = 0.95294117647
    background_gray = {"red":gray_val,"blue":gray_val,"green":gray_val}
    range1 = {"sheetId":0,"startRowIndex":9,"endRowIndex":11,
                "startColumnIndex":0,"endColumnIndex":1}
    range2 = {"sheetId":0,"startRowIndex":9,"endRowIndex":10,
                "startColumnIndex":0,"endColumnIndex":NUM_PLAYERS+1}
    range3 = {"sheetId":0,"startRowIndex":9,"endRowIndex":11+NUM_PLAYERS,
                "startColumnIndex":3,"endColumnIndex":NUM_PLAYERS+1}
    cell = {"userEnteredFormat":{"backgroundColor":background_gray}}
    repeat_cell = {"range":range1, "cell": cell, "fields":"userEnteredFormat(backgroundColor)"}
    requests.append({"repeatCell": repeat_cell})
    repeat_cell = {"range":range2, "cell": cell, "fields":"userEnteredFormat(backgroundColor)"}
    requests.append({"repeatCell": repeat_cell})
    repeat_cell = {"range":range3, "cell": cell, "fields":"userEnteredFormat(backgroundColor)"}
    requests.append({"repeatCell": repeat_cell})
    
    # Fix background borders
    solid_bg_gray = {"style": "SOLID", "color": background_gray}
    update_borders = {"range":range1,"innerVertical":solid_bg_gray,
                    "innerHorizontal":solid_bg_gray}
    requests.append({"updateBorders":update_borders})
    update_borders = {"range":range2,"innerVertical":solid_bg_gray,
                    "innerHorizontal":solid_bg_gray,"left":solid_bg_gray}
    requests.append({"updateBorders":update_borders})
    update_borders = {"range":range3,"innerVertical":solid_bg_gray,
                    "innerHorizontal":solid_bg_gray,"right":solid_bg_gray,
                    "bottom":solid_bg_gray}
    requests.append({"updateBorders":update_borders})

    # Execute changes
    batch_res = bot.memory["sheet"].batchUpdate(spreadsheetId = ID,body = {"requests": requests}).execute()
    
    return ID
'''
Generates a generic draft sheet and returns the spreadsheet ID.
'''

def write_player(bot, cell, player, color):
    ID = bot.memory["sheetID"]
    color = {"red":   color[0],
             "green": color[1],
             "blue":  color[2]}
    celldata = {"userEnteredFormat":{"backgroundColor":color},
                "userEnteredValue":{"stringValue":player}}
    update_cells = {"rows": [{"values": [celldata]}],
            "fields": "userEnteredFormat(backgroundColor),userEnteredValue",
            "start": {"sheetId": 0, "rowIndex": cell[0], "columnIndex": cell[1]}}
    requests = [{"updateCells":update_cells}]
    batch_res = bot.memory["sheet"].batchUpdate(spreadsheetId = ID, body={"requests":requests}).execute()
'''
Given a cell, player, and their color, writes that player's name
and sets the background color to the cell.
'''
