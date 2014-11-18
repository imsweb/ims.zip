from five import grok
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone import utils
from Products.Five.browser import BrowserView
from zope.app.container.interfaces import INameChooser
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.event import notify
from zope.component import getUtility
from zope.lifecycleevent import ObjectModifiedEvent
import mimetypes, zipfile, os

from ims.zip.interfaces import IZipFolder

grok.templatedir('.')

class Unzipper(grok.View):
  grok.name('unzip')
  grok.context(IZipFolder)
  grok.require('cmf.ModifyPortalContent')
  template = ViewPageTemplateFile("unzipper.pt")

  def __call__(self):
    form = self.request.form
    if 'form.submitted' in form:
      zipf = self.request.form.get('file','')
      force_files = self.request.form.get('force_files',False)
      return self.unzip(zipf,force_files)
    return self.template()

  def unzip(self, zipf, force_files=False):
    portal = getUtility(ISiteRoot)
    zipper = zipfile.ZipFile(zipf, 'r')

    for name in zipper.namelist():
      path,file_name = os.path.split(name)
      if file_name:
        stream = zipper.read(name)
        curr = self.context
        for folder in [f for f in path.split('/') if f]:
          try:
            curr = curr[folder]
          except KeyError:
            curr.invokeFactory('Folder',folder)
            curr = curr[folder]
            curr.setTitle(folder)
            curr.reindexObject()
        
        content_type = mimetypes.guess_type(file_name)[0] or ""
        self.factory(file_name, content_type, stream, curr, force_files)
        
        self.context.plone_utils.addPortalMessage(PloneMessageFactory(u'Zip file imported'))
    self.request.response.redirect(self.context.absolute_url(),trusted=True)
    
  def factory(self, name, content_type, data, container, force_files):
      ctr = getToolByName(self.context, 'content_type_registry')
      type_ = force_files and 'File' or ctr.findTypeName(name.lower(), '', '') or 'File'
      
      normalizer = getUtility(IFileNameNormalizer)
      chooser = INameChooser(self.context)
      newid = chooser.chooseName(normalizer.normalize(name), self.context.aq_parent)
      
      obj = utils._createObjectByType(type_, container, newid)
      mutator = obj.getPrimaryField().getMutator(obj)
      mutator(data, content_type=content_type)
      obj.setTitle(name)
      obj.reindexObject()

      notify(ObjectInitializedEvent(obj))
      notify(ObjectModifiedEvent(obj))