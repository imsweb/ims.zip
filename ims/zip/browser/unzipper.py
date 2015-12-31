import plone.api
from plone.directives import form
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone import utils
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from StringIO import StringIO
from zope.container.interfaces import INameChooser
from z3c.form import button
from zope.event import notify
from zope.component import getUtility
from zope.lifecycleevent import ObjectModifiedEvent
import mimetypes, zipfile, os

from ims.zip import _
from ims.zip.interfaces import IZipFolder, IUnzipForm

class Unzipper(form.SchemaForm):
  ignoreContext = True

  schema = IUnzipForm

  @button.buttonAndHandler(_(u'Unzip'))
  def unzipper(self, action):
    """ unzip contents """
    data, errors = self.extractData()
    if errors:
      self.status = self.formErrorsMessage
      return
    zipf = data['file']
    self.unzip(zipf,force_files=True)

    IStatusMessage(self.request).addStatusMessage(_(u"Your content has been imported."),"info")
    return self.request.response.redirect(self.context.absolute_url())

  def unzip(self, zipf, force_files=False):
    portal = getUtility(ISiteRoot)
    zipper = zipfile.ZipFile(StringIO(zipf.data), 'r')

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
    self.request.response.redirect(self.context.absolute_url())

  def factory(self, name, content_type, data, container, force_files):
      ctr = getToolByName(self.context, 'content_type_registry')
      type_ = force_files and 'File' or ctr.findTypeName(name.lower(), '', '') or 'File'

      normalizer = getUtility(IFileNameNormalizer)
      chooser = INameChooser(self.context)
      newid = chooser.chooseName(normalizer.normalize(name), self.context.aq_parent)

      obj = plone.api.content.create(container=container, type=type_, id=newid, title=name)
      primary_field = IPrimaryFieldInfo(obj)
      primary_field.value.filename = name