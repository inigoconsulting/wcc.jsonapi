from five import grok
from zope.publisher.interfaces import IRequest
from Products.CMFCore.interfaces import ISiteRoot
import Acquisition
from Products.ATContentTypes.interfaces.news import IATNewsItem
import json
from plone.uuid.interfaces import IUUID
from AccessControl import Unauthorized
from wcc.jsonapi.interfaces import ISignatureService
from zope.component import getUtility

class APIRoot(Acquisition.Implicit, grok.MultiAdapter):
    grok.adapts(ISiteRoot, IRequest)
    grok.name('api')

    def __init__(self, context, request):
        self.context = context
        self.request = request

class V10(Acquisition.Implicit, grok.MultiAdapter):
    grok.adapts(APIRoot, IRequest)
    grok.name('1.0')

    def __init__(self, context, request):
        self.context = context
        self.request = request

class V10JSON(grok.View):
    grok.baseclass()
    grok.context(V10)

    def render(self):
        url = self.request.getURL()
        ss = ISignatureService(self.context)
        if ss.validate_params(url, self.request.form):
            self.request.response.setHeader('Content-Type','application/json')
            return json.dumps(self.json(),indent=4)
        raise Unauthorized('Unauthorized')

class News(V10JSON):
    def json(self):
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
        brains = self.context.portal_catalog(**params)

        result = []
        for brain in brains[:20]:
            obj = brain.getObject()
            item = {
                'uuid': IUUID(obj),
                'title': brain.Title,
                'description': brain.Description,
                'images': {},
                'date': brain.Date,
                'text': obj.getText(),
                'image_caption': obj.getField('imageCaption').get(obj),
                'state': brain.review_state
            }

            if getattr(brain.modified, 'isoformat', None):
                item['modified'] = brain.modified.isoformat()
            else:
                item['modified'] = brain.modified.ISO8601()
            if obj.getField('image').get(obj):
                scales = obj.unrestrictedTraverse('@@images')
                item['images']['mini'] = scales.scale('image',
                        scale='mini').url
                item['images']['large'] = scales.scale('image',
                        scale='large').url
            result.append(item)
        return result