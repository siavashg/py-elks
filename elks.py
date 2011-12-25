import urllib2
import logging
import base64
import json
import sys
from urllib import urlencode

class Number():
    api = None
    id = None
    active = False
    country = None
    number = None
    sms_callback_url = None
    voice_callback_url = None
    capabilities = list()

    def _set(self, **kwargs):
        for key, value in kwargs.iteritems():
            # Translate non-descriptive 46elks arguments
            key = 'sms_callback_url' if str(key) == 'sms_url' else key
            key = 'voice_callback_url' if str(key) == 'voice_start' else key

            setattr(self, key, value)

    def __init__(self, api, **kwargs):
        self.api = api
        self._set(**kwargs)

    def __repr__(self):
        return str(dict(api=self.api,
                    id=self.id,
                    active=self.active,
                    country=self.country,
                    number=self.number,
                    capabilities=self.capabilities))

    def modify(self,
               sms_callback_url=None,
               voice_callback_url=None):

        sms_callback_url = sms_callback_url or self.sms_callback_url
        voice_callback_url = voice_callback_url or self.voice_callback_url

        data = self.api.modifyNumber(id=self.id,
                                     sms_callback_url=sms_callback_url,
                                     voice_callback_url=voice_callback_url)

        if not data:
            return False

        self._set(**data)
        return True

    def sendMessage(self, receiver, message):
        return self.api.sendMessage(sender=self.number,
                                    receiver=receiver,
                                    message=message)

class SMS():
    api = None
    sender = None
    receiver = None
    message = None

    def __init__(self, api, **kwargs):
        for key, value in kwargs.iteritems():
            key = 'sender' if str(key) == 'from' else key
            key = 'receiver' if str(key) == 'to' else key
            setattr(self, key, value)


class API():
    base_url = 'https://api.46elks.com/a1'
    realm = '46elks API'
    username = None
    password = None

    def __init__(self, username, password, base_url=None, realm=None):
        self.username = username
        self.password = password
        self.base_url = base_url or self.base_url
        self.base_url = base_url or self.base_url

        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm=self.realm,
                                  uri=self.base_url,
                                  user=self.username,
                                  passwd=self.password)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

    def getNumbers(self, active_only=False):
        service_url = '/Numbers'
        request = urllib2.Request(self.base_url + service_url)
        f = self._open(request)
        response = json.loads(f.read())
        logging.debug(response)

        numbers = list()
        if response.has_key('data'):
            for number in response['data']:
                data = dict([(str(k), v) for k, v in number.items()])
                if active_only and data['active'] == 'no':
                    continue
                numbers.append(Number(api=self, **data))

        return numbers

    def getNumber(self, number):
        numbers = self.getNumbers()
        if not numbers:
            return None

        for n in numbers:
            if n.number == number:
                return n

    def sendMessage(self, sender, receiver, message):
        service_url = '/SMS'
        data = {
            'to': receiver,
            'from': sender,
            'message': message
        }

        request = urllib2.Request(self.base_url + service_url)
        f = self._open(request, data)
        response = json.loads(f.read())
        logging.debug(response)

        data = dict([(str(k), v) for k, v in response.items()])
        return SMS(api=self, **data)

    def allocateNumber(self,
                       country='se',
                       sms_callback_url=None,
                       voice_callback_url=None):

        service_url = '/Numbers'
        data = dict(
            country = country,
            sms_url = sms_callback_url,
            voice_start = voice_callback_url)

        request = urllib2.Request(self.base_url + service_url)
        f = self._open(request, data)
        response = json.loads(f.read())
        logging.debug(response)

        data = dict([(str(k), v) for k, v in response.items()])
        return Number(api=self, **data)

    def modifyNumber(self,
                     id,
                     sms_callback_url=None,
                     voice_callback_url=None):

        service_url = '/Numbers/%s' % id
        data = dict(
            sms_url = sms_callback_url,
            voice_start = voice_callback_url)

        request = urllib2.Request(self.base_url + service_url)
        f = self._open(request, data)
        response = json.loads(f.read())

        logging.debug(response)
        data = dict([(str(k), v) for k, v in response.items()])
        return data


    def _open(self, request, data=None):
        if data is not None:
            r_data = dict()
            for key, value in data.iteritems():
                value = 'yes' if value == True else value
                value = 'no' if value == False else value
                if value is not None:
                    r_data[key] = value

            request.add_data(urlencode(r_data))
            logging.debug(request.data)

        try:
            f = urllib2.urlopen(request)
            logging.debug('URL: %s' % f.geturl())
        except IOError, e:
            logging.error(e)
            logging.error('Invalid API credentials')
            sys.exit(1)
        return f
