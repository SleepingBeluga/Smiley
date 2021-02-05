import os.path, datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account as s_a

SECRET = os.path.join(os.getcwd(), "gsecret.json")
SCOPES = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/documents']

c = s_a.Credentials.from_service_account_file(SECRET, scopes=SCOPES)

service = build('docs', 'v1', credentials=c)
drive_service = build('drive', 'v3', credentials=c)

async def nick_log(turns, text_style_ranges, name):
    drive_response = drive_service.files().copy(fileId='1Orc1lONIhJKPfJSuHvFh9rbwQfJikEjrYsAuvrJzt9A', body={'name': name}).execute()
    id = drive_response.get('id')
    perm_result = drive_service.permissions().create(fileId=id,body={"type":"anyone","role":"reader"}).execute()

    requests = []
    for i, turn in enumerate(turns[::-1]):
        if i and i % 50 == 0:
            service.documents().batchUpdate(documentId=id, body={'requests': requests}).execute()
            requests = []
        offset = len(turn['author']) + 2
        requests.append({
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': turn['author'] + '\n'
            }
        })
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': offset - 1
                },
                'textStyle': {
                    'foregroundColor': {
                        'color': {
                            'rgbColor': {
                                'red':   0.35,
                                'green': 0.35,
                                'blue':  0.35
                            }
                        }
                    }
                },
                'fields': 'foregroundColor'
            }
        })
        requests.append({
            'insertText': {
                'location': {
                    'index': offset
                },
                'text': turn['text'] + '\n'
            }
        })
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': offset,
                    'endIndex': offset + len(turn['text'])
                },
                'textStyle': {
                    'foregroundColor': {
                        'color': {
                            'rgbColor': {
                                'red':   0,
                                'green': 0,
                                'blue':  0
                            }
                        }
                    }
                },
                'fields': 'foregroundColor'
            }
        })
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': offset,
                    'endIndex': offset + len(turn['text'])
                },
                'paragraphStyle': {
                    'indentStart': {
                        'magnitude': 18,
                        'unit': 'PT'
                    },
                    'indentFirstLine': {
                        'magnitude': 18,
                        'unit': 'PT'
                    },
                },
                'fields': 'indentStart,indentFirstLine'
            }
        })
        turn_num = len(turns) - 1 - i
        for style in text_style_ranges[str(turn_num)]:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': style['start'] + offset,
                        'endIndex': style['end'] + offset
                    },
                    'textStyle': {
                        style['type']: True
                    },
                    'fields': style['type']
                }
            })
    if len(requests):
        service.documents().batchUpdate(documentId=id, body={'requests': requests}).execute()

    return f'https://docs.google.com/document/d/{id}'

async def new_log_doc(memory, name, players):
    # Call the Docs API
    memory['docs'] = service.documents()

    # Create a doc
    title = name + "-" + datetime.datetime.now().isoformat()
    doc = {
        'name': title
    }
    drive_response = drive_service.files().copy(fileId='1c_6Y-9hREBtbhradT4gKSIQMRKCE9ZjlVU1O0jfPeFA', body=doc).execute()

    # Retrieve doc's ID
    ID = drive_response.get('id')

    # Give public permissions
    view = {"type":"anyone","role":"reader"}
    perm_result = drive_service.permissions().create(fileId=ID,body=view).execute()

    #Provide output: the doc ID and the last index number
    out = []
    out.append(ID)
    out.append(1)

    return out

# Takes the recorded string of text and inserts it into the Doc, formatting along the way
async def add_text(inp, postStart, nameEnd, text, ind):
    request = []
    lineDelay = 0
    for index in range(len(postStart)-1):
        txt = {
            'insertText': {
                'location': {
                    'index': postStart[index] + lineDelay
                },
                'text': text[postStart[index] - 1:postStart[index + 1] - 1]
            }
        }
        postStart[index] = postStart[index] + lineDelay
        nameEnd[index] = nameEnd[index] + lineDelay
        request.append(txt)
        lineDelay += 2

    request += [
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': inp[1],
                    'endIndex': inp[1] + len(text)
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
        }
    ]

    for x in range(len(postStart)-1):
        insert = {
            'updateTextStyle': {
                'range': {
                    'startIndex': postStart[x],
                    'endIndex': nameEnd[x]
                },
                'textStyle': {
                    'bold': True
                },
                'fields': 'bold'
            }
        }
        insert2 = {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': postStart[x],
                    'endIndex': nameEnd[x]
                },
                'paragraphStyle': {
                    'spaceAbove': {
                        'magnitude': 7.0,
                        'unit': 'PT'
                    },
                    'spaceBelow': {
                        'magnitude': 7.0,
                        'unit': 'PT'
                    }
                },
                'fields': 'spaceAbove,spaceBelow'
            }
        }
        request.append(insert)
        request.append(insert2)

    if ind[0] != []:
        for cell in ind[0]:
            insert = {
                'updateTextStyle': {
                    'range': {
                        'startIndex': cell[0] + 2*cell[1],
                        'endIndex': cell[2] + 2*cell[1]
                    },
                    'textStyle': {
                        'bold': True
                    },
                    'fields': 'bold'
                }
            }
            request.append(insert)

    if ind[1] != []:
        for cell in ind[1]:
            insert = {
                'updateTextStyle': {
                    'range': {
                        'startIndex': cell[0] + 2*cell[1],
                        'endIndex': cell[2] + 2*cell[1]
                    },
                    'textStyle': {
                        'bold': True
                    },
                    'fields': 'bold'
                }
            }
            request.append(insert)

    if ind[2] != []:
        for cell in ind[2]:
            insert = {
                'updateTextStyle': {
                    'range': {
                        'startIndex': cell[0] + 2 * cell[1],
                        'endIndex': cell[2] + 2 * cell[1]
                    },
                    'textStyle': {
                        'italic': True
                    },
                    'fields': 'italic'
                }
            }
            request.append(insert)

    if ind[3] != []:
        for cell in ind[3]:
            insert = {
                'updateTextStyle': {
                    'range': {
                        'startIndex': cell[0] + 2 * cell[1],
                        'endIndex': cell[2] + 2 * cell[1]
                    },
                    'textStyle': {
                        'underline': True
                    },
                    'fields': 'underline'
                }
            }
            request.append(insert)

    if ind[4] != []:
        for cell in ind[4]:
            insert = {
                'updateTextStyle': {
                    'range': {
                        'startIndex': cell[0] + 2 * cell[1],
                        'endIndex': cell[2] + 2 * cell[1]
                    },
                    'textStyle': {
                        'strikethrough': True
                    },
                    'fields': 'strikethrough'
                }
            }
            request.append(insert)

    cutoff = {
        'deleteContentRange': {
            'range': {
                'startIndex': postStart[len(postStart) - 1] + lineDelay - 2,
                'endIndex': 2151 + len(text) - 2
            }
        }
    }
    request.append(cutoff)

    do = service.documents().batchUpdate(documentId=inp[0], body={'requests': request}).execute()
    inp[1] += len(text)

    return inp
