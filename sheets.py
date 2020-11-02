import pickle, os.path, datetime, random, difflib
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
    elif NUM_PLAYERS == 7:
        column_headers = ["","Supreme","Great","Good","Moderate","Modest","Poor","Least"]
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
                "startColumnIndex":0,"endColumnIndex":NUM_PLAYERS+4}
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
    delete_cols = {"range": {"sheetId":0,"dimension":"COLUMNS","startIndex":NUM_PLAYERS+4}}
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
                "startColumnIndex":0,"endColumnIndex":NUM_PLAYERS+4}
    range3 = {"sheetId":0,"startRowIndex":9,"endRowIndex":11+NUM_PLAYERS,
                "startColumnIndex":3,"endColumnIndex":NUM_PLAYERS+4}
    range4 = {"sheetId":0,"startRowIndex":0,"endRowIndex":10,
                "startColumnIndex":NUM_PLAYERS+1,"endColumnIndex":NUM_PLAYERS+4}
    cell = {"userEnteredFormat":{"backgroundColor":background_gray}}
    repeat_cell = {"range":range1, "cell": cell, "fields":"userEnteredFormat(backgroundColor)"}
    requests.append({"repeatCell": repeat_cell})
    repeat_cell = {"range":range2, "cell": cell, "fields":"userEnteredFormat(backgroundColor)"}
    requests.append({"repeatCell": repeat_cell})
    repeat_cell = {"range":range3, "cell": cell, "fields":"userEnteredFormat(backgroundColor)"}
    requests.append({"repeatCell": repeat_cell})
    repeat_cell = {"range":range4, "cell": cell, "fields":"userEnteredFormat(backgroundColor)"}
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
    update_borders = {"range":range4,"innerVertical":solid_bg_gray,
                    "innerHorizontal":solid_bg_gray,"right":solid_bg_gray,
                    "bottom":solid_bg_gray}
    requests.append({"updateBorders":update_borders})

    # Execute changes
    batch_res = memory["sheet"].batchUpdate(spreadsheetId = ID,body = {"requests": requests}).execute()

    return ID
'''
Generates a generic draft sheet and returns the spreadsheet ID.
'''

async def write_cell_request(memory, cell, content, bgcolor, fgcolor):
    '''Given a cell, contents, and colors, returns a request to write contents
    and sets colors for that cell.
    '''
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
    return {"updateCells":update_cells}

async def execute_updates(memory, reqs):
    '''Takes in an array of updates returned from write_cell_request and applies them
    '''
    ID = memory['sheetID']
    batch_res = memory["sheet"].batchUpdate(spreadsheetId = ID, body={"requests":reqs}).execute()

# - - - - More weird channel stuff below. Should hopefully still work when copy-pasted

ID1 = '1Foxb_C_zKvLuSMOB4HN5tRMpVwtPrkq6tdlokKSgEqY'
# This is now the permanent trigger doc
TriggerID = '1bWigKxmpEObOWTP0uRA_xwmMnF3Lpk9ZQer5msl6WnA'
TriggerSuggestionsID = '1IZmqUsIXKejHKycZoUEz-agXiQYgoxedz_XF80x8zF4'
DetailID = '1aHyZ7c7TIgt903mPinOakrgli2WZu5IRtiGYPCnCqDE'
SuggestionID = '1kWxWhvKzAYl98nuvgCQOchw7mgH7aecyB82hSwMtatQ'
TradingDatabaseID = '1T7-1FfEsXGH0zKrIeTi21BDPS1xIEDOpStMu0rOV4bs'
CapesDatabaseID = '1_syrsmptzWG0u3xdY3qzutYToY1t3I8s6yaryIpfckU'

async def newgame(name, GM, type):

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Campaigns!A1:E1000').execute()
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

async def category(game):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Campaigns!A1:E1000').execute()
    values = result.get('values', [])

    game = game.lower()

    for row in values:
        if str(row[0]) == str('#' + game):
            return str(row[3])

    return None

async def gamecheck(name, game):

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Campaigns!A1:E1000').execute()
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
                                range='Campaigns!A1:E1000').execute()
    values = result.get('values', [])
    game = game.lower()

    for row in values:
        if str(row[0]) == str('#' + game):
            return row[1]

    return ''

async def addlink(name, campaign, link):

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Campaigns!A1:E1000').execute()
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
                                range='Campaigns!A1:E1000').execute()
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

async def increment(category, value):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TriggerID,
                                range='Count & Frontpage!A7:B18').execute()
    values = result.get('values', [])
    index = 6

    for row in values:
        if str(row[0]).lower() == category:
            current = float(row[1])
            new = current + value
            celldata = {"userEnteredValue": {"numberValue": new}}
            update_cells = {"rows": [{"values": [celldata]}],
                            "fields": "userEnteredValue",
                            "start": {"sheetId": 0, "rowIndex": index, "columnIndex": 1}}
            requests = [{"updateCells": update_cells}]
            batch_res = sheet.batchUpdate(spreadsheetId=TriggerID, body={"requests": requests}).execute()
            return True
        else:
            index += 1

    return False

async def claim(number, game, player, desc):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TriggerID,
                                range='Triggers!A1:B100').execute()
    values = result.get('values', [])
    num_rows = 0
    for row in values:
        if str(row[0]) != "":
            num_rows += 1
        else:
            break
    index = number
    if index > num_rows or index < 0:
        return "Can't find a trigger at index " + str(index)

    if index == 0:
        index = random.randrange(0, rowNum)
    else:
        # Because the user specifies from 1
        index -= 1

    text = str(values[index][0])
    author = str(values[index][1])
    del_req = {
        "deleteDimension": {
            "range": {
                "sheetId": 1146274495, # Triggers
                "dimension": "ROWS",
                "startIndex": index,
                "endIndex": index+1
            }
        }
    }

    result = sheet.values().get(spreadsheetId=TriggerID,
                                range='Used!A1:B1000').execute()
    values = result.get('values', [])
    num_used_rows = 1
    for row in values[1:]:
        if str(row[0]) != "" or str(row[1]) != "":
            num_used_rows += 1
        else:
            break

    insert_req = {
        "insertDimension": {
            "range": {
                "sheetId": 239110446,
                "dimension": "ROWS",
                "startIndex": num_used_rows,
                "endIndex": num_used_rows + 1
            },
            "inheritFromBefore": True
        }
    }

    data_to_paste = '<table><tr><td>' + game + \
                          '</td><td>' + text + \
                          '</td><td>' + author + \
                          '</td><td>' + player + \
                          '</td><td>' + desc + '</tr></table>'

    paste_req = {
        "pasteData": {
            "coordinate": {
                "sheetId": 239110446,
                "rowIndex": num_used_rows,
                "columnIndex": 0
            },
            "data": data_to_paste,
            "type": "PASTE_VALUES",
            "html": True
        }
    }
    reqs = [del_req, insert_req, paste_req]
    batch_res = sheet.batchUpdate(spreadsheetId=TriggerID, body={"requests": reqs}).execute()
    return "Claimed trigger " + str(number) + " at used " + str(num_used_rows) + "!"

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

async def luck(column, beta = False, search = None):
    sheet = service.spreadsheets()
    index = None
    if not beta:
        result = sheet.values().get(spreadsheetId=DetailID,
                                    range='LUCK!A1:F79').execute()
    else:
        result = sheet.values().get(spreadsheetId=SuggestionID,
                                    range='Perks and Flaws!A1:F79').execute()
    values = result.get('values', [])
    relevantLuck = []
    count = 1
    # Go through specific column
    for row in values[1:]:
        count += 1
        if not row:
            break
        try:
            if not str(row[1+column]) == "":
                found = str(row[1+column])
                relevantLuck.append(found)
                if search:
                    distance = difflib.SequenceMatcher(None, search.lower(), found[:len(search)].lower()).ratio()
                    if distance > 0.85:
                        return found
        except:
            pass

    if not search:
        index = random.randint(0, len(relevantLuck)-1)
    if index:
        return str(relevantLuck[index])

async def skill(skill, arg):
    sheet = service.spreadsheets()
    index = None
    result = sheet.values().get(spreadsheetId=SuggestionID,
                                range='Skills!A2:R100').execute()
    values = result.get('values', [])
    category = skill
    skill = skill.lower()
    arg = arg.lower()
    if skill in ["list", "brawn", "athletics", "dexterity", "social", "wits", "knowledge", "guts"]:
        # We are listing skills!
        statBreakdown = {
            "brawn": [],
            "athletics": [],
            "dexterity": [],
            "social": [],
            "wits": [],
            "knowledge": [],
            "guts": []
        }
        for row in values:
            for key in statBreakdown.keys():
                if key == str(row[1]).lower():
                    statBreakdown[key] += [str(row[0])]
                if key == str(row[2]).lower():
                    statBreakdown[key] += [str(row[0])]

        if skill in ["brawn", "athletics", "dexterity", "social", "wits", "knowledge", "guts"]:
            string = category + ":\n"
            listing = ""
            for i in statBreakdown[skill]:
                listing += i + ", "
            string += listing[:-2]
            return string
        else:
            string = ""
            for category in ["Brawn", "Athletics", "Dexterity", "Social", "Wits", "Knowledge", "Guts"]:
                string += category + ":\n"
                listing = ""
                for i in statBreakdown[category.lower()]:
                    listing += i + ", "
                string += listing[:-2] + "\n\n"
            return string

    for row in values:
        if skill == str(row[0]).lower():
            # Always start with name and categories
            string = str(row[0]) + "(" + str(row[1])
            if str(row[2]) != "-":
                string += ", " + str(row[2])
            string += ")\n"
            if arg == "basic":
                # Print basic stuff
                string += str(row[3])
                if str(row[16]) == "Y":
                    string += "\n"
                    string += "There is additional information for this skill "
                    string += "that is not stored here, check the Misc doc."
            elif arg == "short":
                string += str(row[4])
            elif arg == "1":
                string += "Pip ●: "
                string += str(row[5])
            elif arg == "2":
                string += "Pip ●●: "
                string += str(row[6])
            elif arg == "3":
                string += "Pip ●●●: "
                string += str(row[7])
            elif arg == "4":
                string += "Pip ●●●●: "
                string += str(row[8])
            elif arg == "5":
                string += "Pip ●●●●●: "
                string += str(row[9])
            elif arg == "specialities" or arg == "speciality":
                special = False
                for x in range(0,6):
                    if str(row[10+x]) != "-":
                        if not special:
                            special = True
                            string += "Specialities:"
                        string += "\n" + str(row[10+x])
            else:
                string = "Do not recognise arguement " + str(arg)
            return string

    return "Haven't added this skill yet"

async def trading_capes():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TradingDatabaseID,
                                range='Capes!A2:K1000').execute()
    values = result.get('values', [])
    allinfo = []
    for row in values:
        try:
            if not str(row[0]) == "":
                allinfo += [ row ]
            else:
                break
        except:
            break

    return allinfo

async def owned_cards():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TradingDatabaseID,
                                range='Owned!A2:B10000').execute()
    values = result.get('values', [])
    allinfo = []
    for row in values:
        try:
            if not str(row[0]) == "":
                allinfo += [ row ]
            else:
                break
        except:
            break

    return allinfo

async def gain_cards(claimer, cards):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TradingDatabaseID,
                                range='Owned!A2:B10000').execute()
    values = result.get('values', [])
    used_rows = 1
    for row in values:
        try:
            if not str(row[0]) == "":
                used_rows += 1
            else:
                break
        except:
            break

    data_to_paste = "<table>"
    for i in cards:
        data_to_paste += "<tr><td>{}</td>".format(claimer)
        data_to_paste += "<td>{}</td></tr>".format(str(i))
    data_to_paste += "</table>"

    paste_req = {
        "pasteData": {
            "coordinate": {
                "sheetId": 1429634698,
                "rowIndex": used_rows,
                "columnIndex": 0
            },
            "data": data_to_paste,
            "type": "PASTE_VALUES",
            "html": True
        }
    }
    reqs = [paste_req]
    batch_res = sheet.batchUpdate(spreadsheetId=TradingDatabaseID, body={"requests": reqs}).execute()


async def move_card_owner(old, new, cards):
    if len(cards) == 0:
        return
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TradingDatabaseID,
                                range='Owned!A2:B10000').execute()
    values = result.get('values', [])
    reqs = []
    for card in cards:
        for row in range(0, len(values)):
            try:
                owner = str(values[row][0])
                c_index = str(values[row][1])
                if owner == old and c_index == str(card):
                    values[row][0] = new
                    reqs += [{
                        "pasteData": {
                            "coordinate": {
                                "sheetId": 1429634698,
                                "rowIndex": row+1,
                                "columnIndex": 0
                            },
                            "data": '<table><tr><td>' + new + '</td></tr></table>',
                            "type": "PASTE_VALUES",
                            "html": True
                        }
                    }]
                    break
            except:
                continue

    batch_res = sheet.batchUpdate(spreadsheetId=TradingDatabaseID, body={"requests": reqs}).execute()

async def remove_cards(owner, cards):
    if len(cards) == 0:
        return
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TradingDatabaseID,
                                range='Owned!A2:B10000').execute()
    values = result.get('values', [])
    rows_to_delete = []
    for card in cards:
        for row in range(0, len(values)):
            try:
                own = str(values[row][0])
                c_index = str(values[row][1])
                if owner == own and c_index == str(card) and not row in rows_to_delete:
                    rows_to_delete += [row]
                    break
            except:
                continue

    if len(rows_to_delete) != len(cards):
        return

    # Delete in reverse order!
    rows_to_delete.sort(reverse=True)
    for i in rows_to_delete:
        del_req = {
            "deleteDimension": {
                "range": {
                    "sheetId": 1429634698, # Triggers
                    "dimension": "ROWS",
                    "startIndex": i+1,
                    "endIndex": i+2
                }
            }
        }
        batch_res = sheet.batchUpdate(spreadsheetId=TradingDatabaseID, body={"requests": [del_req]}).execute()

async def get_battle_stats():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TradingDatabaseID,
                                range='Battle Stats!A2:G20').execute()
    values = result.get('values', [])
    stats = {"classes": {}, "multipliers": {}}
    for i in values[:12]:
        stats["classes"][i[0]] = {}
        stats["classes"][i[0]]["Defend"] = float(i[1])
        stats["classes"][i[0]]["Attack"] = float(i[2])
        stats["classes"][i[0]]["Flee"] = float(i[3])
        stats["classes"][i[0]]["Ambush"] = float(i[4])
        stats["classes"][i[0]]["Health"] = float(i[5])
        stats["classes"][i[0]]["Wits"] = float(i[6])

    for i in values[14:]:
        stats["multipliers"][i[0]] = {}
        stats["multipliers"][i[0]]["Defend"] = float(i[1])
        stats["multipliers"][i[0]]["Attack"] = float(i[2])
        stats["multipliers"][i[0]]["Wits"] = float(i[3])

    return stats

async def waiting_triggers():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TriggerSuggestionsID,
                                range='Trigger Suggestions!A2:C1000').execute()
    values = result.get('values', [])
    triggers = {}
    for row in values:
        try:
            if str(row[0]) != "":
                trigger = str(row[0])
                reviewers = []
                try:
                    r_string = str(row[1]) # Don't let people review their own trigger
                    r_string = r_string.split("(")[-1]
                    r_string = r_string.split(")")[0]
                    if r_string.strip() != "":
                        reviewers += [r_string.strip()]
                except:
                    pass
                try:
                    r_string = str(row[2])
                    r_string = r_string.split(",")
                    for i in r_string:
                        if i != "":
                            reviewers += [i.strip()]
                except:
                    pass
                triggers[trigger] = reviewers
            else:
                break
        except:
            continue
    return triggers

async def get_relevant_trigger_row(triggers, trigger):
    for row in range(0, len(triggers)):
        try:
            if str(triggers[row][0]) != "":
                if str(triggers[row][0]) == trigger:
                    return row
            else:
                break
        except:
            continue

async def submit_trigger(trigger, u_id, u_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TriggerSuggestionsID,
                                range='Trigger Suggestions!A2:F1000').execute()
    triggers = result.get('values', [])
    index = 0
    for row in triggers:
        try:
            if str(row[0]) == "":
                break
            else:
                index += 1
        except:
            break # Assuming that failure also means empty row!

    data_to_paste = '<table><tr><td>' + trigger + \
                          '</td><td>' + u_name + ' (' + str(u_id) + ')</tr></table>'

    paste_req = {
        "pasteData": {
            "coordinate": {
                "sheetId": 1029421998,
                "rowIndex": index+1,
                "columnIndex": 0
            },
            "data": data_to_paste,
            "type": "PASTE_VALUES",
            "html": True
        }
    }
    reqs = [paste_req]
    batch_res = sheet.batchUpdate(spreadsheetId=TriggerSuggestionsID, body={"requests": reqs}).execute()

async def approve_trigger(trigger, u_id, u_name, comments=""):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TriggerSuggestionsID,
                                range='Trigger Suggestions!A2:F1000').execute()
    triggers = result.get('values', [])
    index = await get_relevant_trigger_row(triggers, trigger)
    ids = ""
    users = ""
    comm = ""
    try:
        if str(triggers[index][2]) != "":
            ids = str(triggers[index][2]) + ", "
    except:
        pass
    try:
        if str(triggers[index][3]) != "":
            users = str(triggers[index][3]) + ", "
    except:
        pass
    try:
        comm = str(triggers[index][4])
        if comments != "" and comm != "":
            comm += ", "
    except:
        pass
    ids += str(u_id)
    users += str(u_name)
    if comments != "":
        comm += comments + " - " + str(u_name)

    data_to_paste = '<table><tr><td>' + ids + \
                          '</td><td>' + users + \
                          '</td><td>' + comm + '</tr></table>'

    paste_req = {
        "pasteData": {
            "coordinate": {
                "sheetId": 1029421998,
                "rowIndex": index+1,
                "columnIndex": 2
            },
            "data": data_to_paste,
            "type": "PASTE_VALUES",
            "html": True
        }
    }
    reqs = [paste_req]
    batch_res = sheet.batchUpdate(spreadsheetId=TriggerSuggestionsID, body={"requests": reqs}).execute()


async def critique_trigger(trigger, u_id, u_name, comments):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TriggerSuggestionsID,
                                range='Trigger Suggestions!A2:F1000').execute()
    triggers = result.get('values', [])
    index = await get_relevant_trigger_row(triggers, trigger)
    ids = ""
    users = ""
    comm = ""
    try:
        if str(triggers[index][2]) != "":
            ids = str(triggers[index][2]) + ", "
    except:
        pass
    try:
        users = str(triggers[index][3])
    except:
        pass
    try:
        comm = str(triggers[index][4])
        if comments != "" and comm != "":
            comm += ", "
    except:
        pass
    ids += str(u_id)
    if comments != "":
        comm += comments + " - " + str(u_name)

    data_to_paste = '<table><tr><td>' + ids + \
                          '</td><td>' + users + \
                          '</td><td>' + comm + '</tr></table>'

    paste_req = {
        "pasteData": {
            "coordinate": {
                "sheetId": 1029421998,
                "rowIndex": index+1,
                "columnIndex": 2
            },
            "data": data_to_paste,
            "type": "PASTE_VALUES",
            "html": True
        }
    }
    reqs = [paste_req]
    batch_res = sheet.batchUpdate(spreadsheetId=TriggerSuggestionsID, body={"requests": reqs}).execute()

async def cape(name):
    sheet = service.spreadsheets()
    index = None
    result = sheet.values().get(spreadsheetId=CapesDatabaseID,
                                range='Non-Canon!A2:K1833').execute()
    values = result.get('values', [])
    count = 0

    for row in values:
        try:
            if not str(row[0]) == "":
                if str(row[0]) == name:
                    return row
                count += 1
        except:
            pass

    if name == "":
        num = random.randrange(0,count)
        return values[num]

    return None

async def documents():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Documents!A2:C1000').execute()
    values = result.get('values', [])

    data = {}
    for row in values:
        try:
            if not str(row[0]) == "":
                data[str(row[0])] = str(row[1])
        except:
            pass

    return data

async def add_document(doc, link, submitter):
    sheet = service.spreadsheets()
    index = 1
    result = sheet.values().get(spreadsheetId=ID1,
                                range='Documents!A2:C1000').execute()
    values = result.get('values', [])
    for row in values:
        try:
            if not str(row[0]) == "":
                index += 1
            else:
                break
        except:
            break

    data_to_paste = '<table><tr><td>' + doc + \
                          '</td><td>' + link + \
                          '</td><td>' + submitter + '</td></tr></table>'

    paste_req = {
        "pasteData": {
            "coordinate": {
                "sheetId": 2032145493,
                "rowIndex": index,
                "columnIndex": 0
            },
            "data": data_to_paste,
            "type": "PASTE_VALUES",
            "html": True
        }
    }
    reqs = [paste_req]
    batch_res = sheet.batchUpdate(spreadsheetId=ID1, body={"requests": reqs}).execute()


# ...sorry about the mess X|
