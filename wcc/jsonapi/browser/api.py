from five import grok
from zope.publisher.interfaces import IRequest
from Products.CMFCore.interfaces import ISiteRoot
import Acquisition
from Products.ATContentTypes.interfaces.news import IATNewsItem
import json

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
        self.request.response.setHeader('Content-Type','application/json')
        return json.dumps(self.json(),indent=4)

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
                'title': brain.Title,
                'description': brain.Description,
                'images': {},
                'date': brain.Date,
                'text': obj.getText()
            }
            if obj.getField('image').get(obj):
                scales = obj.unrestrictedTraverse('@@images')
                item['images']['mini'] = scales.scale('image',
                        scale='mini').url
            result.append(item)
        return result
