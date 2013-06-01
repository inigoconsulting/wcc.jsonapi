from five import grok
from wcc.jsonapi.interfaces import ISignatureService
from wcc.jsonapi.interfaces import IAPIClient
import requests

class APIQueryError(Exception):
    pass

class V10APIClient(object):
    grok.implements(IAPIClient)

    def __init__(self, context, endpoint):
        self.context = context
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        self.endpoint = endpoint
        
    def news(self, language=None, category=None, limit=20):
        api_url = '%s/1.0/news' % (self.endpoint)
        ss = ISignatureService(self.context)

        params = {}
        if language is not None:
            params['language'] = language.strip()
            
        if limit is not None:
            params['limit'] = limit
        if category:
            params['category'] = category.strip()

        params = ss.sign_params(api_url, params)
        resp = requests.get(api_url, params=params)
        out = resp.json()

        if 'error' in out:
            raise APIQueryError('%s : %s' % (
                out['error'],
                out['error-message']
            ))

        return out

    def activities(self, language=None, category=None, limit=20):
        api_url = '%s/1.0/activities' % (self.endpoint)
        ss = ISignatureService(self.context)

        params = {}

        if language is not None:
            params['language'] = language.strip()

        if limit is not None:
            params['limit'] = limit

        if category:
            params['category'] = category.strip()

        params = ss.sign_params(api_url, params)
        resp = requests.get(api_url, params=params)
        out = resp.json()

        if 'error' in out:
            raise APIQueryError('%s : %s' % (
                out['error'],
                out['error-message']
            ))

        return out

    def translation(self, content):
        api_url = '%s/1.0/translations/%s' % (self.endpoint, content)
        ss = ISignatureService(self.context)
        params = ss.sign_params(api_url, {})
        resp = requests.get(api_url, params=params)
        out = resp.json()

        if 'error' in out:
            raise APIQueryError('%s : %s' % (
                out['error'],
                out['error-message']
            ))

        return out


    def activity(self, activity):
        api_url = '%s/1.0/activities/%s' % (self.endpoint, activity)
        ss = ISignatureService(self.context)
        params = ss.sign_params(api_url, {})
        resp = requests.get(api_url, params=params)
        out = resp.json()

        if 'error' in out:
            raise APIQueryError('%s : %s' % (
                out['error'],
                out['error-message']
            ))

        return out


    def activity_news(self, activity, category=None, language=None, limit=20):
        api_url = '%s/1.0/activities/%s/news' % (self.endpoint, activity)
        ss = ISignatureService(self.context)

        params = {}
        if limit is not None:
            params['limit'] = limit

        if category is not None:
            params['category'] = category

        if language is not None:
            params['language'] = language

        params = ss.sign_params(api_url, params)
        resp = requests.get(api_url, params=params)
        out = resp.json()

        if 'error' in out:
            raise APIQueryError('%s : %s' % (
                out['error'],
                out['error-message']
            ))
        return out

