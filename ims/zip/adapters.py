from zope import interface, component
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.blob.interfaces import IATBlob, IATBlobImage
from Products.ATContentTypes.interfaces.file import IATFile
from ims.zip.interfaces import IZippable

class AdapterBase(object):
    """ provide __init__ """
    def __init__(self, context):
        self.context = context
    def getExtension(self):
      return ''
    def getZippable(self):
      return ''

class ATBlobZip(AdapterBase):
    """ for blobbable files """
    def getZippable(self):
      # plone.app.blob does the icky work for us even though they hate this method
      # it does load everything in mem but don't we have to?
      return self.context.get_data()

class ATFileZip(AdapterBase):
    """ for ATFile type """
    def getZippable(self):
      return self.context.get_data()

class ATImageZip(AdapterBase):
    """ for ATImage type """
    def getZippable(self):
      if IATBlobImage.providedBy(self.context):
          return self.context.getPrimaryField().tag(self.context)
      else:
          return self.context.get_data()

class ATDocumentZip(AdapterBase):
     """ for ATDocument type"""
     def getZippable(self):
        wrapper = '<html><body>%s</body></html>'
        return wrapper % self.context.getText()
     def getExtension(self):
        return '.html'