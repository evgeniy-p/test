import requests
import json

url = "https://ringme.atlassian.net/rest/api/3/search"
url2 = "https://ringme.atlassian.net//rest/api/3/issue/"
headers = {
   "Accept": "application/json",
    "Content-Type": "application/json"
}


def write_content(content, newfile):
    if content.get('content'):
        for text in content['content']:
            if text.get('content'):
                for inf in text['content']:
                    for txt in inf['content']:
                        if txt.get('text'):
                            newfile.write(txt['text'].encode('utf-8') + '\n')
                        else:
                            print(txt)
            else:
                if text.get('text'):
                    newfile.write(text['text'].encode('utf-8') + '\n')
    else:
        print(content)


with open('teleo_open_tickets', 'w') as newfile:
    for results in [0, 50, 100, 150, 200, 250, 300, 350, 400]:
        payload = json.dumps({"jql": "project = RWI", "startAt": results, "maxResults": 50,
                              "fields": ['resolution'], "fieldsByKeys": False})
        response = requests.request("POST", url, headers=headers, data=payload,
                                    auth=('e.putilin@ringme.ru', 'x7t5uDhB92RdOdMSOrKeF44A'))
        for issue in json.loads(response.text)["issues"]:
            if not issue['fields']['resolution']:
                print('Open: ' + issue['key'])
                response2 = requests.request("get", url2 + issue['key'], headers=headers,
                                             auth=('e.putilin@ringme.ru', 'x7t5uDhB92RdOdMSOrKeF44A'))
                newfile.write('------------------------------------------------------\n')
                newfile.write(issue['key'] + ' ')
                newfile.write(json.loads(response2.text)['fields']['summary'].encode('utf-8'))
                newfile.write('\n')
                newfile.write('------------------------------------------------------\n')

                for info in json.loads(response2.text)['fields']['description']['content']:
                    write_content(info, newfile)

                newfile.write('------------------------------------------------------\n')

                for comment in json.loads(response2.text)['fields']['comment']['comments']:
                    newfile.write('----------------\n')
                    newfile.write(comment['updateAuthor']['displayName'].encode('utf-8'))
                    newfile.write('\n')
                    for content in comment['body']['content']:
                        write_content(content, newfile)

                newfile.write('----------------\n')
            else:
                print('Closed: ' + issue['key'])


