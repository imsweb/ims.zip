import zipfile, os
from five import grok
from zope import interface, component
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getUtility

from ims.zip.interfaces import IZippable, IZipFolder

grok.templatedir('.')

class ZipPrompt(grok.View):
  """ confirm zip """
  grok.name('zipfiles')
  grok.context(IZipFolder)
  grok.require('ims.CanZip')
  grok.template('zipper')

class Zipper(grok.View):
  """ Zips content to a temp file """
  grok.name('zipconfirm')
  grok.context(IZipFolder)
  grok.require('ims.CanZip')

  def __call__(self):
    self.request.response.setHeader('Content-Type','application/zip')
    self.request.response.setHeader('Content-disposition','attachment;filename=%s.zip' % self.context.getId())
    return self.zipfiles()
  
  def zipfiles(self):
    """ Zip all of the content in this location (context)"""
    from io import BytesIO
    stream = BytesIO()
    
    self.zipFilePairs(stream)
    return stream.getvalue()

  def zipFilePairs(self, fstream):
    """Return the path and file stream of all content we find here"""
    base_path = '/'.join(self.context.getPhysicalPath())+'/' # the path in the ZCatalog
    portal = component.getUtility(ISiteRoot)
    cat = getToolByName(portal,'portal_catalog')
    filepairs = []
    
    zipper = zipfile.ZipFile(fstream, 'w', zipfile.ZIP_DEFLATED)
    registry = getUtility(IRegistry)
    ignored_types = registry.get('ims.zip.ignored_types',[])

    content = cat(path=base_path,object_provides=IZippable.__identifier__)
    for c in content:
      rel_path = c.getPath().split(base_path)[1:] or [c.getId] # the latter if the root object has an adapter
      if rel_path and c.portal_type not in ignored_types:
        zip_path = os.path.join(*rel_path)
        adapter = component.queryAdapter(c.getObject(),IZippable)
        stream = adapter.getZippable()
        ext = adapter.getExtension()
        zipper.writestr(zip_path+ext, stream)
    zipper.close()