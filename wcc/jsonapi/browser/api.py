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
from wcc.activity.interfaces import IActivityRelation
from Acquisition import aq_base

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
#        url = self.request.getURL()
#        ss = ISignatureService(self.context)
#        if not ss.validate_params(url, self.request.form):
#            raise Unauthorized('Unauthorized')
#
        self.request.response.setHeader('Content-Type','application/json')
        return json.dumps(self.json(),indent=4)

class Activities(V10JSON):

    def json(self):

        brains = self.context.portal_catalog(portal_type='wcc.activity.activity')

        result = []
        for brain in brains:
            obj = brain.getObject()
            item = {
                'uuid': IUUID(obj),
                'title': obj.Title(),
                'description': obj.Description(),
                'images': {},
                'date': obj.Date(),
                'text': obj.text,
                'image_caption': obj.imageCaption,
            }

            wftool = self.context.portal_workflow
            item['state'] = wftool.getInfoFor(obj, 'review_state')

            if getattr(obj.modified(), 'isoformat', None):
                item['modified'] = obj.modified().isoformat()
            else:
                item['modified'] = obj.modified().ISO8601()

            if getattr(aq_base(obj), 'image', None):
                scales = obj.unrestrictedTraverse('@@images')
                mini = scales.scale('image', scale='mini')
                if mini:
                    item['images']['mini'] = mini.url
                large = scales.scale('image', scale='large')
                if large:
                    item['images']['large'] = large.url
            result.append(item)
        return result


class News(V10JSON):

    def _news_for_activity(self):
        activity_uuid = self.request.get('activity', '')
        brains = self.context.portal_catalog(UID=activity_uuid)
        if not brains:
            return []

        activity = brains[0].getObject()
        objs = IActivityRelation(activity).related_news()
        category = self.request.get('category', '')
        if category:
            subjects = [s.lower() for s in obj.Subjects()]
            return [obj for obj in objs if category.lower() in subjects]
        return objs

    def json(self):
        activity_uuid = self.request.get('activity', '')
        if activity_uuid:
            objs = self._news_for_activity()
        else:
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
            item = {
                'uuid': IUUID(obj),
                'title': obj.Title(),
                'description': obj.Description(),
                'images': {},
                'date': obj.Date(),
                'text': obj.getText(),
                'image_caption': obj.getField('imageCaption').get(obj),
            }

            wftool = self.context.portal_workflow

            item['state'] = wftool.getInfoFor(obj, 'review_state')

            if getattr(obj.modified(), 'isoformat', None):
                item['modified'] = obj.modified().isoformat()
            else:
                item['modified'] = obj.modified().ISO8601()
            if obj.getField('image').get(obj):
                scales = obj.unrestrictedTraverse('@@images')
                item['images']['mini'] = scales.scale('image',
                        scale='mini').url
                item['images']['large'] = scales.scale('image',
                        scale='large').url
            result.append(item)
        return result
