from five import grok
from zope.publisher.interfaces import IRequest
from Products.CMFCore.interfaces import ISiteRoot
import Acquisition
from Products.ATContentTypes.interfaces.news import IATNewsItem
import json
from plone.uuid.interfaces import IUUID
from AccessControl import Unauthorized
from wcc.jsonapi.interfaces import ISignatureService, IJsonProvider
from zope.component import getUtility
from wcc.activity.interfaces import IActivityRelation
from Acquisition import aq_base
from wcc.jsonapi.content import api as model

class V10JSON(grok.View):
    grok.baseclass()
    grok.name('index')

    def render(self):
        url = self.request.getURL().replace('/@@index', '')
        ss = ISignatureService(self.context)

        if not ss.validate_params(url, self.request.form):
            self.request.response.setHeader('Content-Type','application/json')
            return json.dumps({
                'error-code': '403',
                'error': 'Unauthorized'
            })

        self.request.response.setHeader('Content-Type','application/json')
        return json.dumps(self.json(),indent=4)

class Activities(V10JSON):
    grok.context(model.ActivityCollection)

    def json(self):
        brains = self.context.portal_catalog(portal_type='wcc.activity.activity')
        result = []
        for brain in brains:
            obj = brain.getObject()
            item = IJsonProvider(obj).to_dict()
            result.append(item)
        return result

class Activity(V10JSON):
    grok.context(model.Activity)

    def json(self):
        return IJsonProvider(self.context.obj).to_dict()


class News(V10JSON):
    grok.context(model.NewsCollection)

    def json(self):
        activity_uuid = self.request.get('activity', '')
        params = {
            'object_provides': IATNewsItem.__identifier__,
            'sort_on': 'Date',
            'sort_order': 'descending',
            'Language': 'all',
        }
        category = self.request.get('category', '')
        if category:
            params['Subject'] = category.strip()
        params['Language'] = self.request.get('language', 'all')
        objs = [
            brain.getObject() for brain in self.context.portal_catalog(
                **params)
        ]

        result = []
        for obj in objs[:20]:
            item = IJsonProvider(obj).to_dict()
            result.append(item)

        return result
