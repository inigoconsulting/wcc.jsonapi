from five import grok
import hashlib
from datetime import datetime
from DateTime import DateTime
from dateutil.parser import parse as parse_dt
import copy
import os
import hmac
import urlparse
from wcc.jsonapi.interfaces import ISignatureService
import urllib
from zope.interface import Interface

class SignatureService(grok.Adapter):
    grok.implements(ISignatureService)
    grok.context(Interface)

    def __init__(self, context):
        self.context = context
        self.secret = os.environ.get('WCC_JSONAPI_SECRET', None)
        if self.secret is None:
            raise Exception('WCC_JSONAPI_SECRET is not set')

    def sign_params(self, url, parameters=None):
        parameters = parameters or {}
        params = copy.copy(parameters)
        if 'auth_sig' in params:
            del params['auth_sig']

        timestamp = '%sGMT+0' % datetime.utcnow().isoformat()
        params['timestamp'] = timestamp
        key_values = sorted(params.items(), key=lambda x:x[0])
        qs = urllib.urlencode(key_values)
        if '?' not in url:
            url += '?'
        sig = hmac.new(self.secret, url + qs, hashlib.sha1).hexdigest()
        params['auth_sig'] = sig
        return params

    def validate_params(self, url, parameters=None, tolerance=300):
        parameters = parameters or {}
        param = copy.copy(parameters)
    
        timestamp = param.get('timestamp', None)

        if not timestamp:
            return False

        timestamp_dt = parse_dt(timestamp)
        delta = datetime.utcnow() - DateTime(timestamp_dt).utcdatetime()
        if delta.seconds > tolerance:
            return False
    
        auth_sig = param.get('auth_sig', None) 

        if not auth_sig:
            return False
            
        del param['auth_sig']

        key_values = sorted(param.items(), key=lambda x:x[0])
        qs = urllib.urlencode(key_values)
    
        if '?' not in url:
            url += '?'

        sig = hmac.new(self.secret, url + qs, hashlib.sha1).hexdigest()
    
        return sig == auth_sig
    

if __name__ == '__main__':
    s = SignatureService()
    url = 'http://localhost.local'
    p = {'a':'b','c':'d'}
    param = s.sign_params(url, p)
    assert s.validate_params(url, param) == True
