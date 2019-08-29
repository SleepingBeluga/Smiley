import pickle, os.path, datetime, random
from googleapiclient.discovery import build
from google.oauth2 import service_account as s_a

SECRET = os.path.join(os.getcwd(), "gsecret.json")
SCOPES = ['https://www.googleapis.com/auth/drive']

c = s_a.Credentials.from_service_account_file(SECRET, scopes=SCOPES)

service = build('sheets', 'v4', credentials=c)
drive_service = build('drive', 'v3', credentials=c)

async def new_blank_sheet(memory, NUM_PLAYERS):
    # Call the Sheets API
    memory["sheet"] = service.spreadsheets()

    # Create a spreadsheet
    now = datetime.datetime.now()
    todays_date = now.strftime("%b %d, %Y")
    title = "Pact Dice Draft " + todays_date
    spreadsheet = {"properties": {"title": title}}
    spreadsheet = memory["sheet"].create(body = spreadsheet, fields="spreadsheetId").execute()

    # Get the ID
    ID = spreadsheet.get("spreadsheetId")

    # Give public permissions
    view = {"type":"anyone","role":"reader"}
    perm_result = drive_service.permissions().create(fileId=ID,body=view).execute()

    # Write draft table
    # Write column headers
    if NUM_PLAYERS == 4:
        column_headers = ["","Supreme","Good","Modest","Least"]
    elif NUM_PLAYERS == 5:
        column_headers = ["","Supreme","Good","Moderate","Modest","Least"]
    elif NUM_PLAYERS == 6:
        column_headers = ["","Supreme","Great","Good","Modest","Poor","Least"]
    else:
        column_headers = [""] + [str(n) for n in list(range(1,4))]
    values = [column_headers]
    body = {"values": values}
    write_res = memory["sheet"].values().update(spreadsheetId=ID,range="A1",valueInputOption="RAW",body=body).execute()
    # Write row headers
    row_headers = ["","Puissance","Longevity","Access",
                    "Executions","Research","Schools",
                    "Priority","Family"]
    values = [row_headers]
    body = {"values": values, "majorDimension":"COLUMNS"}
    write_res = memory["sheet"].values().update(spreadsheetId=ID,range="A1",valueInputOption="RAW",body=body).execute()

    # Write karma table
    column_headers = ["", "White","Black"]
    body = {"values": [column_headers]}
    write_res = memory["sheet"].values().update(spreadsheetId=ID,range="A11",valueInputOption="RAW",body=body).execute()

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
    batch_res = memory["sheet"].batchUpdate(spreadsheetId = ID,body = {"requests": requests}).execute()

    return ID
'''
Generates a generic draft sheet and returns the spreadsheet ID.
'''

async def write_cell(memory, cell, content, bgcolor, fgcolor):
    ID = memory["sheetID"]
    bgcolor = {"red": bgcolor[0],
               "green": bgcolor[1],
               "blue":  bgcolor[2]}
    fgcolor = {"red": fgcolor[0],
               "green": fgcolor[1],
               "blue":  fgcolor[2]}
    celldata = {"userEnteredFormat":{"backgroundColor":bgcolor,
                "textFormat": {'foregroundColor':fgcolor}},
                "userEnteredValue":{"stringValue":content}}
    update_cells = {"rows": [{"values": [celldata]}],
                    "fields": "userEnteredFormat(backgroundColor,textFormat(foregroundColor)),userEnteredValue",
                    "start": {"sheetId": 0, "rowIndex": cell[0], "columnIndex": cell[1]}}
    requests = [{"updateCells":update_cells}]
    batch_res = memory["sheet"].batchUpdate(spreadsheetId = ID, body={"requests":requests}).execute()
'''
Given a cell, contents, and colors, writes contents
and sets the colors for the cell.
'''

# - - - - More weird channel stuff below. Should hopefully still work when copy-pasted

ID1 = '1Foxb_C_zKvLuSMOB4HN5tRMpVwtPrkq6tdlokKSgEqY'
# Note: this is a temporary sheet to use so that the actual trigger doc
# is not interfered with
TriggerID = '1bWigKxmpEObOWTP0uRA_xwmMnF3Lpk9ZQer5msl6WnA'
DetailID = '1kWxWhvKzAYl98nuvgCQOchw7mgH7aecyB82hSwMtatQ'

async def newgame(name, GM, type):

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Campaigns!A1:E100').execute()
    values = result.get('values', [])

    rowNum = 0

    name = name.lower()

    for row in values:
        if row[0] != "":
            rowNum = rowNum + 1

    cell = (rowNum,0)
    celldata = {"userEnteredValue": {"stringValue": name}}
    update_cells = {"rows": [{"values": [celldata]}],
                    "fields": "userEnteredValue",
                    "start": {"sheetId": 0, "rowIndex": cell[0], "columnIndex": cell[1]}}
    requests = [{"updateCells": update_cells}]
    batch_res = sheet.batchUpdate(spreadsheetId=ID1, body={"requests": requests}).execute()

    cell = (rowNum,1)
    celldata = {"userEnteredValue": {"stringValue": GM}}
    update_cells = {"rows": [{"values": [celldata]}],
                    "fields": "userEnteredValue",
                    "start": {"sheetId": 0, "rowIndex": cell[0], "columnIndex": cell[1]}}
    requests = [{"updateCells": update_cells}]
    batch_res = sheet.batchUpdate(spreadsheetId=ID1, body={"requests": requests}).execute()

    cell = (rowNum, 2)
    celldata = {"userEnteredValue": {"stringValue": 'Y'}}
    update_cells = {"rows": [{"values": [celldata]}],
                    "fields": "userEnteredValue",
                    "start": {"sheetId": 0, "rowIndex": cell[0], "columnIndex": cell[1]}}
    requests = [{"updateCells": update_cells}]
    batch_res = sheet.batchUpdate(spreadsheetId=ID1, body={"requests": requests}).execute()


    cell = (rowNum, 3)
    celldata = {"userEnteredValue": {"stringValue": type}}
    update_cells = {"rows": [{"values": [celldata]}],
                    "fields": "userEnteredValue",
                    "start": {"sheetId": 0, "rowIndex": cell[0], "columnIndex": cell[1]}}
    requests = [{"updateCells": update_cells}]
    batch_res = sheet.batchUpdate(spreadsheetId=ID1, body={"requests": requests}).execute()

async def gamecheck(name, game):

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Campaigns!A1:E100').execute()
    values = result.get('values', [])

    check = False

    game = game.lower()

    for row in values:
        if str(row[0]) == str('#' + game):
            if str(row[1]) == str(name):
                check = True

    return check

# Find the owner of a specified game
async def ownercheck(game):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Campaigns!A1:E100').execute()
    values = result.get('values', [])
    game = game.lower()

    for row in values:
        if str(row[0]) == str('#' + game):
            return row[1]

    return ''

async def addlink(name, campaign, link):

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Campaigns!A1:E100').execute()
    values = result.get('values', [])

    rowNum = 0

    for row in values:
        if str(row[1]) == str(name) and str(row[0]) == ('#'+campaign):
            cell = (rowNum, 4)
            celldata = {"userEnteredValue": {"stringValue": link}}
            update_cells = {"rows": [{"values": [celldata]}],
                            "fields": "userEnteredValue",
                            "start": {"sheetId": 0, "rowIndex": cell[0], "columnIndex": cell[1]}}
            requests = [{"updateCells": update_cells}]
            batch_res = sheet.batchUpdate(spreadsheetId=ID1, body={"requests": requests}).execute()
            return False
        else:
            rowNum = rowNum + 1
    return True

async def changeState(name,yesno):

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Campaigns!A1:E100').execute()
    values = result.get('values', [])

    rowNum = 0

    name = name.lower()

    for row in values:
        if str(row[0]) == str('#' + name):
            break
        else:
            rowNum = rowNum + 1

    cell = (rowNum, 2)
    celldata = {"userEnteredValue": {"stringValue": yesno}}
    update_cells = {"rows": [{"values": [celldata]}],
                    "fields": "userEnteredValue",
                    "start": {"sheetId": 0, "rowIndex": cell[0], "columnIndex": cell[1]}}
    requests = [{"updateCells": update_cells}]
    batch_res = sheet.batchUpdate(spreadsheetId=ID1, body={"requests": requests}).execute()

async def trigger(index):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TriggerID,
                                range='Triggers!A1:B100').execute()
    values = result.get('values', [])

    rowNum = 0
    for row in values:
        if str(row[0]) != "":
            rowNum += 1
        else:
            break
    
    if index > rowNum or index < 0:
        # Can not find a trigger at this index
        return ''
    
    if index == 0:
        index = random.randrange(0, rowNum)
    else:
        # Because the user specifies from 1
        index -= 1

    return str(index + 1) + ": " + str(values[index][0])

async def used(index):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TriggerID,
                                range='Used!A1:B1000').execute()
    values = result.get('values', [])

    usedTriggers = []
    # Go through and build 
    for row in values[1:]:
        if not row:
            break
        if str(row[1]) != "":
            usedTriggers += [str(row[1])]
    
    if index > len(usedTriggers) or index < 0:
        # Can not find a trigger at this index
        return ''
    
    if index == 0:
        index = random.randrange(0, len(usedTriggers))
    else:
        index -= 1

    return str(index + 1) + ": " + str(usedTriggers[index])

async def luck(column):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=DetailID,
                                range='Perks and Flaws #2!A1:F79').execute()
    values = result.get('values', [])

    relevantLuck = []
    count = 1
    # Go through specific column
    for row in values[1:]:
        count += 1
        if not row:
            break
        try:
            if str(row[1+column]) != "":
                relevantLuck += [str(row[1+column])]
        except:
            # Don't do anything
            print("Failed to execute luck("+str(column)+") on line "+str(count))
    
    index = random.randint(0, len(relevantLuck)-1)
    return str(relevantLuck[index])


# ...sorry about the mess X|

# Little experiment here:
def capename():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId='1JyuNC8OfUD1zj1R9eF97L6IKSdQ6978QJqq_fmkyTc4',
                                range='B2:B205').execute()
    values = result.get('values', [])

    string = str(values[random.randint(2,200)])
    return string[2:(len(string)-2)]

def name():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId='1JyuNC8OfUD1zj1R9eF97L6IKSdQ6978QJqq_fmkyTc4',
                                range='C2:E205').execute()
    values = result.get('values', [])

    gender = random.randint(0,1)

    string1 = str(values[random.randint(0,200)][gender])
    string2 = str(values[random.randint(0,200)][2])
    string2 = string2[0].upper() + string2[1:len(string2)].lower()

    return string1 + " " + string2