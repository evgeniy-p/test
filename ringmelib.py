#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import requests
import time
import logging
import json
import urllib
import sys

requests.packages.urllib3.disable_warnings()


class UnauthorizedException(Exception):
    """Возникает, если приложению не удается получить токен"""
    pass


class NotFoundException(Exception):
    """Возникает при ошибке 404"""
    pass


class ApiException(Exception):
    """Возникает при ошибке 400, сгенерированного API"""


class BadResponseException(Exception):
    """Возникает, при любом ошибочном ответе, кроме ошибок с авторизацией, 400 и 404"""
    pass


class RingmeTrustedApp(object):
    """
    Методы класса представляют обертку методов get(), put(), delete(), update()  модуля "requests"
    с автоматически обновлением/получением токена и кешированием его в файле.

    Можно считать, что если методы не вернули Exception, то запрос прошел успешно.
    В возвращаемом значении будет словарь(или массив словарей при get() на список) с параметрами ответа
    """

    def __init__(self, api_host, api_path, api_id, api_secret, https_verify=False, profile=False):
        self._api_host = api_host
        self.api_path = api_path
        self._api_id = api_id
        self._api_secret = api_secret
        self._token = None
        self._token_file = "token_saved.txt"
        self._check_file = True
        self._headers = None
        self.https_verify = https_verify
        self.profile = profile

    def _token_get(self):

        if self._token:
            return

        script_dir = sys.path[0]
        token_file = script_dir + "/" + self._token_file
        token_file_content = ""

        # сначала попробуем взять из файла
        if self._check_file:
            logging.debug('получение access token из файла "{0}"'.format(token_file))
            try:
                with open(token_file) as f:
                    token_file_content = f.read()
            except IOError:
                pass

            find = re.search("^(\S+)\t(\d+)$", token_file_content)
            if find:
                expires_in = find.group(2)
                if expires_in and expires_in.isdigit():
                    if int(expires_in) > time.time():
                        self._token = find.group(1)
                        logging.debug("access token успешно получен из файла")
                        return
                    else:
                        logging.debug("время действиия сохраненного access token истекло")

        # получение нового токена с сервера
        logging.debug("получение access token с сервера {0}".format(self._api_host))
        request_url = "{host}/oauth/token".format(host=self._api_host)
        body = {
            'grant_type': 'client_credentials',
            'client_id': self._api_id,
            'client_secret': self._api_secret,
        }
        response = requests.post(request_url, data=body, verify=False)
        if response.status_code == 200:
            self._token = response.json().get('access_token', None)
            expires_in = response.json().get('expires_in', None)
            if self._token and expires_in and isinstance(expires_in, int):
                try:
                    with open(token_file, "w") as f:
                        f.write("{0}\t{1}".format(self._token, int(time.time()) + expires_in))
                        self._check_file = True
                except IOError as e:
                    logging.error('невозможно сохранить access token в файле "{0}": {1}'.format(token_file, e))
                    pass
            return
        elif response.status_code == 401:
            logging.error('ошибка авторизации: {error}'.format(error=response.json().get('error', '')))
        else:
            logging.error('неизвестная ошибка: #{error}'.format(error=response.status_code))

    def _time_check(fn):

        def decorated(self, *args, **kwargs):
            if self.profile:
                time_start = time.time()
            ret = fn(self, *args, **kwargs)
            if self.profile:
                logging.debug("время ответа: {duration}".format(duration=time.time() - time_start))
            return ret

        return decorated

    def _token_check(fn):

        def decorated(self, *args, **kwargs):
            last_response = None
            while True:
                self._token_get()
                if not self._token:
                    logging.error('отсутствует access token')
                    raise UnauthorizedException()
                else:
                    logging.debug("access token: {0}".format(self._token))
                self._headers = {
                    'Content-type': 'application/json',
                    'Authorization': 'Bearer {access_token}'.format(access_token=self._token)
                }
                response = fn(self, *args, **kwargs)
                if response is not None and hasattr(response, 'status_code'):
                    last_response = response.status_code
                if last_response == 401:
                    logging.error('ошибка авторизации: {error}'.format(error=response.json()))
                    self._check_file = False  # обновить токен, а не брать сохраненный
                    self._token = None
                    continue
                elif last_response in (200, 201):
                    return response.json()
                elif last_response == 204:
                    return {}
                elif last_response == 404:
                    raise NotFoundException("ресурс не найден {url}".format(url=response.url))
                elif last_response == 400:
                    message = ""
                    try:
                        message = response.json()["message"]
                    except:
                        pass
                    raise ApiException(message)
                elif last_response:
                    message = ""
                    try:
                        message = str(response.json())
                    except:
                        message = response.content
                        pass
                    raise BadResponseException("получена ошибка №{error_number}: {message}".format(error_number=last_response, message=message))
                else:
                    raise BadResponseException("неизвестный ответ сервера")
                break
            raise UnauthorizedException()

        return decorated

    def get_url(self, path, filter_dict=None):
        ret = "{host}/{api_path}/{resource_path}".format(host=self._api_host, api_path=self.api_path.strip('/'), resource_path=path.lstrip('/'))
        if isinstance(filter_dict, dict):
            ret = "{ret}/?{filter_str}".format(ret=ret.rstrip('/'), filter_str=urllib.urlencode(filter_dict, True))
        return ret

    @_token_check
    @_time_check
    def get(self, path, filter_dict=None):
        request_url = self.get_url(path, filter_dict)
        return requests.get(request_url, headers=self._headers, verify=self.https_verify)

    @_token_check
    @_time_check
    def post(self, path, payload_dict):
        request_url = self.get_url(path)
        return requests.post(request_url, headers=self._headers, data=json.dumps(payload_dict), verify=self.https_verify)

    @_token_check
    @_time_check
    def put(self, path, payload_dict):
        request_url = self.get_url(path)
        return requests.put(request_url, headers=self._headers, data=json.dumps(payload_dict), verify=self.https_verify)

    @_token_check
    @_time_check
    def delete(self, path):
        request_url = self.get_url(path)
        return requests.delete(request_url, headers=self._headers, verify=self.https_verify)


if __name__ == "__main__":
    from conf import Conf
    import datetime
    '''
    class Conf(object):
        API_HOST = "https://conftest.ringme.ru"
        API_PATH = "/test/ver1.0"
        APP_ID = "805cd9dc264746b8935c64ab2752342"
        APP_SECRET = "a6c51e3fbe434ad284356ca8f323222"
    '''
    trustedApp = RingmeTrustedApp(Conf.API_HOST, Conf.API_PATH, Conf.APP_ID, Conf.APP_SECRET)
    try:
        pbx_client_id = 12

        # список всех добавочных
        extension_list = trustedApp.get('/client/{pbx_client_id}/extension/'.format(pbx_client_id=pbx_client_id))
        print "Все Добавочные:\n"
        for extension in extension_list:
            print "\tдобавочный номер {ext_number} (id {ext_id})".format(ext_number=extension["name"], ext_id=extension["id"])

        # добавочный с именем 000*000
        filter_dict = {"name": "000*000"}
        extension_list = trustedApp.get('/client/{pbx_client_id}/extension/'.format(pbx_client_id=pbx_client_id), filter_dict)
        if len(extension_list) > 0:
            print "добавочный номер {ext_number} (id {ext_id}); label: {label}".format(ext_number=extension_list[0]["name"], ext_id=extension_list[0]["id"], label=extension_list[0]["label"])
            # обвновить параметр "label"
            update_data = {"label": "hello world! {0}".format(datetime.datetime.now())}
            updated_extension_data = trustedApp.put('/client/{pbx_client_id}/extension/{ext_id}'.format(pbx_client_id=pbx_client_id, ext_id=extension_list[0]["id"]), update_data)
            print "новые данные {ext_number} (id {ext_id}); label: {label}".format(ext_number=updated_extension_data["name"], ext_id=updated_extension_data["id"], label=updated_extension_data["label"])

    except UnauthorizedException as e:
        print "Не пройти OAuth2.0 авторизацию"
    except BadResponseException as e:
        print str(e)
    except NotFoundException as e:
        print str(e)
