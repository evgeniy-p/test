import requests
import json
import os
import re

request_url = "https://apiproxy.telphin.ru/oauth/token"
body = {
            'grant_type': 'client_credentials',
            'client_id': '0b34602057414e2daeddcc8289245c09',
            'client_secret': '5e7aad30eba34b20b0407aeab38b7053',
        }


response = requests.post(request_url, data=body, verify=True)
if response.status_code == 200:
    token = response.json().get('access_token', None)


class API:
    def __init__(self,token):
        self.token = token

    def take_params(self, method):
        ret = requests.get("https://apiproxy.telphin.ru//test/ver1.0/{method}".format(method=method),
                           headers={'Content-type': 'application/json',
                                    'Authorization': 'Bearer {access_token}'.format(access_token=self.token)},
                           verify=True)
        return ret


os.chdir('/var/log/')
file_list = os.popen('ls').read().split('\n')[:-1]
kam_file = [txt for txt in file_list if re.match('kamailio.log', txt)]

numbers = []
for txt in kam_file:
    a = os.popen("grep -P '\\[\\d{{5,}}\\]' /var/log/{txt_file} | gawk -F' ' '{{print $15}}' | sort | uniq".format(
        txt_file=txt)).read().split('\n')[:-1]
    numbers.append(set(a))

test = API(token)
for i in numbers[0].intersection(*numbers[1:]):
    try:
        ret1 = test.take_params('/admin/did/?name={number}'.format(number=i[1:-1]))
        print(i[1:-1])
        print('client:', ret1.json()[0]["client_id"], 'id:', ret1.json()[0]["id"])
        ret2 = test.take_params('/admin/did/{did}/registration/status/'.format(did=ret1.json()[0]["id"]))
        print(ret2.json()['registered'])
    except Exception as e:
        print('number ', i[1:-1], 'is not found or not correct', ret1.json())



