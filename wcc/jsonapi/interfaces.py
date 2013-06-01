from zope.interface import Interface

class IProductSpecific(Interface):
    pass

class ISignatureService(Interface):

    def sign_param(url, param):
        pass

    def verify_param(url, param):
        pass


class IAPIClient(Interface):

    def news(language, category):
        pass


    def activity_news(language, category):
        pass

    def activities(language, category):
        pass

class IJsonProvider(Interface):

    def to_dict():
        pass

    def json():
        pass

