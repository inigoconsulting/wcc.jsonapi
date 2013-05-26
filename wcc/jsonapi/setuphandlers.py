from collective.grok import gs
from wcc.jsonapi import MessageFactory as _

@gs.importstep(
    name=u'wcc.jsonapi', 
    title=_('wcc.jsonapi import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('wcc.jsonapi.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
