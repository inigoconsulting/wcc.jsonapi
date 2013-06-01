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
from Acquisition import aq_base

class V10JSON(grok.View):
    grok.name('index')
    grok.context(model.Context)

    def render(self):
        url = self.request.getURL().replace('/@@index', '')
        ss = ISignatureService(self.context)

        if not ss.validate_params(url, self.request.form):
            self.request.response.setHeader('Content-Type','application/json')
            return json.dumps({
                'error': '403',
                'error-messagee': 'Unauthorized'
            })

        self.request.response.setHeader('Content-Type','application/json')

        if not getattr(aq_base(self.context), 'query', None):
            return json.dumps({
                'error': '404',
                'error-message': 'Not Found'
            })
        return json.dumps(self.context.query(),indent=4)
