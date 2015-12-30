from zope import interface, component
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.blob.interfaces import IATBlob, IATBlobImage
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.ATContentTypes.interfaces.file import IATFile
from ims.zip.interfaces import IZippable

class AdapterBase(object):
    """ provide __init__ """
    def __init__(self, context):
        self.context = context
    def extension(self):
      return ''
    def zippable(self):
      return ''

class FileZip(AdapterBase):
    """ for ATFile type """
    def zippable(self):
      return self.context.get_data()
    def extension(self):
      id = self.context.getId()
      primary_field = IPrimaryFieldInfo(self.context)
      import pdb; pdb.set_trace()
      fn = self.context.file.filename or id
      return id.split('.')[-1] != fn.split('.')[-1] and '.'+fn.split('.')[-1] or ''

class ImageZip(AdapterBase):
    """ for ATImage type """
    def zippable(self):
      if IATBlobImage.providedBy(self.context):
          primary_field = IPrimaryFieldInfo(self.context)
          return primary_field.value
          #return str(self.context.getPrimaryField().getAccessor(self.context)())
      else:
          return self.context.file.value

class DocumentZip(AdapterBase):
    """ for ATDocument type"""
    def zippable(self):
      template = '<html><body>%(header)s%(description)s%(text)s</body></html>'

      header = self.context.title and '<h1>%s</h1>' % self.context.title or ''
      description = self.context.Description() and '<p class="description">%s</p>' % self.context.description or ''
      text = self.context.text

      html = template % {'header':header,'description':description,'text':text}
      return html
    def extension(self):
      return '.html'