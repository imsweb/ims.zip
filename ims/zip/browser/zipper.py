import zipfile, os
from five import grok
from zope import interface, component
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility

from ims.zip import _
from ims.zip.interfaces import IZippable, IZipFolder

grok.templatedir('.')

def _is_zippable(view):
  return _get_size(view) <= 2*1024.0*1024.0*1024.0 # 2 GB

def _get_size(view):    
  registry = getUtility(IRegistry)
  portal = component.getUtility(ISiteRoot)
  cat = getToolByName(portal,'portal_catalog')
  
  base_path = '/'.join(view.context.getPhysicalPath())+'/' # the path in the ZCatalog
  ignored_types = registry.get('ims.zip.ignored_types',[])
  ptypes = [ptype for ptype in cat.uniqueValuesFor('portal_type') if ptype not in ignored_types]

  content = cat(path=base_path,object_provides=IZippable.__identifier__,portal_type=ptypes)
  return sum([getattr(b,'get_file_size',0) or 0 for b in content]) # get_file_size is an index of an obj's size() method

class ZipPrompt(grok.View):
  """ confirm zip """
  grok.name('zipfiles')
  grok.context(IZipFolder)
  grok.require('ims.CanZip')
  grok.template('zipper')
  
  def get_size(self):
    return _get_size(self)
  
  def is_zippable(self):
    return _is_zippable(self)
  
  def size_estimate(self):
    return '%.2f MB' % (_get_size(self)/1024.0/1024)

class Zipper(grok.View):
  """ Zips content to a temp file """
  grok.name('zipconfirm')
  grok.context(IZipFolder)
  grok.require('ims.CanZip')

  def __call__(self):
    try:
      self.request.response.setHeader('Content-Type','application/zip')
      self.request.response.setHeader('Content-disposition','attachment;filename=%s.zip' % self.context.getId())
      return self.zipfiles()
    except zipfile.LargeZipFile:
      IStatusMessage(self.request).addStatusMessage(_(u"This folder is too large to be zipped. Try zipping subfolders individually."),"error")
      return self.request.response.redirect(self.context.absolute_url())
  
  def zipfiles(self):
    """ Zip all of the content in this location (context)"""
    if not _is_zippable(self):
      IStatusMessage(self.request).addStatusMessage(_(u"This folder is too large to be zipped. Try zipping subfolders individually."),"error")
      return self.request.response.redirect(self.context.absolute_url())
      
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
    ptypes = [ptype for ptype in cat.uniqueValuesFor('portal_type') if ptype not in ignored_types]

    content = cat(path=base_path,object_provides=IZippable.__identifier__,portal_type=ptypes)
    for c in content:
      rel_path = c.getPath().split(base_path)[1:] or [c.getId] # the latter if the root object has an adapter
      if rel_path and c.portal_type not in ignored_types:
        zip_path = os.path.join(*rel_path)
        adapter = component.queryAdapter(c.getObject(),IZippable)
        stream = adapter.getZippable()
        ext = adapter.getExtension()
        zipper.writestr(zip_path+ext, stream)
    zipper.close()