import pickle, os.path, datetime, random, difflib
from googleapiclient.discovery import build
from google.oauth2 import service_account as s_a

SECRET = os.path.join(os.getcwd(), "gsecret.json")
SCOPES = ['https://www.googleapis.com/auth/drive']

c = s_a.Credentials.from_service_account_file(SECRET, scopes=SCOPES)

service = build('docs', 'v1', credentials=c)
drive_service = build('drive', 'v3', credentials=c)

async def new_log_doc(memory, name, num, players):
    # Call the Sheets API
    memory['docs'] = service.documents()

    # Create a spreadsheet
    title = name + " " + str(num)
    playBill = "Players: "
    for player in players:
        playBill += player + ", "
    playBill = playBill[:-2]
    doc = {
        'title': title
    }
    doc = memory['docs'].create(body=doc).execute()

    # Get the ID
    ID = doc.get("documentId")

    # Give public permissions
    view = {"type":"anyone","role":"reader"}
    perm_result = drive_service.permissions().create(fileId=ID,body=view).execute()

    # Create the template
    template = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': title + '\n' + playBill + '\n\n\"...\"\n\n'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(title)+1
                },
                'textStyle':{
                    'bold': True,
                    'fontSize':{
                        'magnitude': 18,
                        'unit': 'PT'
                    }
                },
                'fields': 'bold, fontSize'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': len(title) + len(playBill)+2,
                    'endIndex': len(title) + len(playBill)+11
                },
                'textStyle':{
                    'italic': True
                },
                'fields': 'italic'
            }
        },
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(title) + len(playBill)+11
                },
                'paragraphStyle': {
                    'alignment': 'CENTER',
                },
                'fields': 'alignment'
            }
        }
    ]
    do = memory['docs'].batchUpdate(documentId=ID, body={'requests': template}).execute()

    out = []
    out.append(ID)
    out.append(len(title) + len(playBill) + 11)

    return out

async def add_post(inp, poster, post):

    post=" ___________________________________________________________________________\n" + poster + "\n" + post + '\n'

    request = [
        {
            'insertText': {
                'location': {
                    'index': inp[1],
                },
                'text': post
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': inp[1]+77,
                    'endIndex': inp[1]+len(poster)+78
                },
                'textStyle': {
                    'bold': True
                },
                'fields': 'bold'
            }
        },
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': inp[1],
                    'endIndex': inp[1]+len(poster)+len(post)-6
                },
                'paragraphStyle': {
                    'spaceAbove': {
                        'magnitude': 0.0,
                        'unit': 'PT'
                    },
                    'spaceBelow': {
                        'magnitude': 7.0,
                        'unit': 'PT'
                    }
                },
                'fields': 'spaceAbove,spaceBelow'
            }
        },
    ]
    do = service.documents().batchUpdate(documentId=inp[0], body={'requests': request}).execute()
    inp[1] += len(post)
    return inp

async def append(inp, post):

    post=post + '\n'

    request = [
        {
            'insertText': {
                'location': {
                    'index': inp[1],
                },
                'text': post
            }
        },
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': inp[1],
                    'endIndex': inp[1]+len(post)-3
                },
                'paragraphStyle': {
                    'spaceAbove': {
                        'magnitude': 0.0,
                        'unit': 'PT'
                    },
                    'spaceBelow': {
                        'magnitude': 7.0,
                        'unit': 'PT'
                    }
                },
                'fields': 'spaceAbove,spaceBelow'
            }
        },
    ]
    do = service.documents().batchUpdate(documentId=inp[0], body={'requests': request}).execute()
    inp[1] += len(post)
    return inp