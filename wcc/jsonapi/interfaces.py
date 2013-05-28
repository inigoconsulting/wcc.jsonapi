from zope.interface import Interface

class IProductSpecific(Interface):
    pass

class ISignatureService(Interface):

    def sign_param(url, param):
        pass

    def verify_param(url, param):
        pass
