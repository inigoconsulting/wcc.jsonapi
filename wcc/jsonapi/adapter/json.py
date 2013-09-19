from five import grok
from wcc.jsonapi.interfaces import IJsonProvider
from plone.uuid.interfaces import IUUID
from Products.CMFCore.interfaces import IDublinCore
from plone.dexterity.interfaces import IDexterityContent
from wcc.activity.content.activity import IActivity
from wcc.document.content.document import IDocument
from Products.ATContentTypes.interfaces.news import IATNewsItem

class BaseJsonProvider(grok.Adapter):
    grok.context(IDublinCore)
    grok.implements(IJsonProvider)

    def __init__(self, context):
        self.context = context

    def to_dict(self):
        obj = self.context

        item = {
            'uuid': IUUID(obj),
            'title': obj.Title(),
            'description': obj.Description(),
            'date': obj.Date(),
        }

        wftool = self.context.portal_workflow

        item['state'] = wftool.getInfoFor(obj, 'review_state')

        if getattr(obj.modified(), 'isoformat', None):
            item['modified'] = obj.modified().isoformat()
        else:
            item['modified'] = obj.modified().ISO8601()
        return item

    def json(self):
        return json.dumps(self.to_dict(), indent=4)

class ActivityJsonProvider(BaseJsonProvider):
    grok.context(IActivity)

    def to_dict(self):
        item = super(ActivityJsonProvider, self).to_dict()

        item['image_caption'] = self.context.imageCaption
        item['image'] = {}
        item['text'] = self.context.text

        scales = self.context.unrestrictedTraverse('@@images')
        mini = scales.scale('image', scale='mini')
        if mini:
            item['image']['mini'] = mini.url
        large = scales.scale('image', scale='large')
        if large:
            item['image']['large'] = large.url

        return item

class NewsJsonProvider(BaseJsonProvider):
    grok.context(IATNewsItem)

    def to_dict(self):
        item = super(NewsJsonProvider, self).to_dict()

        obj = self.context
        item['image_caption'] = obj.getField('imageCaption').get(obj)
        item['image'] = {}
        item['text'] = obj.getText()

        scales = self.context.unrestrictedTraverse('@@images')
        mini = scales.scale('image', scale='mini')
        if mini:
            item['image']['mini'] = mini.url
        large = scales.scale('image', scale='large')
        if large:
            item['image']['large'] = large.url

        return item


class DocumentJsonProvider(BaseJsonProvider):
    grok.context(IDocument)

    def to_dict(self):
        item = super(DocumentJsonProvider, self).to_dict()
        obj = self.context 
        return item
