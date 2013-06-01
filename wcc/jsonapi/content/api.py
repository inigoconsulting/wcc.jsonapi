from five import grok
from zope.publisher.interfaces import IRequest
from Products.CMFCore.interfaces import ISiteRoot
import Acquisition
from zope.component.hooks import getSite

class Context(Acquisition.Implicit):
    pass

class ContentContext(Context):

    def __init__(self, obj):
        self.obj = obj

class AdapterContext(Context, grok.MultiAdapter):
    grok.baseclass()

    def __init__(self, parent, request):
        self.request = request

class APIRoot(AdapterContext):

    # http://site/api

    grok.adapts(ISiteRoot, IRequest)
    grok.name('api')

class V10(AdapterContext):

    # http://site/api/1.0/

    grok.adapts(APIRoot, IRequest)
    grok.name('1.0')

class ActivityCollection(AdapterContext):

    # http://site/api/1.0/activities

    grok.adapts(V10, IRequest)
    grok.name('activities')

    def __getattr__(self, uuid):
        site = getSite()
        brains = site.portal_catalog(UID=uuid)
        if not brains:
            raise AttributeError(uuid)
        return Activity(brains[0].getObject())

class Activity(ContentContext):
    pass

class NewsCollection(AdapterContext):

    # http://site/api/1.0/news

    grok.adapts(V10, IRequest)
    grok.name('news')
