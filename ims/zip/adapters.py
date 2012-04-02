from zope import interface, component
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.blob.interfaces import IATBlob
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
      return self.context.getFile().data

class ATFileZip(AdapterBase):
    """ for ATFile type """
    def getZippable(self):
      return self.context.getFile().data

class ATImageZip(AdapterBase):
    """ for ATImage type """
    def getZippable(self):
      img = self.context.getImage()
      try:
        img = img.getBlob().open('r').read()
      except AttributeError:
        pass
      return img

class ATDocumentZip(AdapterBase):
     """ for ATDocument type"""
     def getZippable(self):
        wrapper = '<html><body>%s</body></html>'
        return wrapper % self.context.getText()
     def getExtension(self):
        return '.html'