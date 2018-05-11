import mimetypes
import os
import zipfile
from StringIO import StringIO

import plone.api
from Products.CMFPlone import utils
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from ims.zip import _
from ims.zip.interfaces import IUnzipForm
from plone.autoform.form import AutoExtensibleForm
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.rfc822.interfaces import IPrimaryFieldInfo
from z3c.form import button, form
from zope.component import getUtility
from zope.container.interfaces import INameChooser


class Unzipper(AutoExtensibleForm, form.Form):
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
        force_files = data['force_files']
        self.unzip(zipf, force_files=force_files)

        plone.api.portal.show_message(_(u"Your content has been imported."), self.request, type="info")
        return self.request.response.redirect(self.context.absolute_url())

    def updateActions(self):
        super(Unzipper, self).updateActions()
        self.actions.values()[0].addClass("context")

    def unzip(self, zipf, force_files=False):
        zipper = zipfile.ZipFile(StringIO(zipf.data), 'r')

        for name in zipper.namelist():
            path, file_name = os.path.split(name)
            if file_name:
                stream = zipper.read(name)
                curr = self.context
                for folder in [f for f in path.split('/') if f]:
                    try:
                        curr = curr[folder]
                    except KeyError:
                        curr.invokeFactory('Folder', folder)
                        curr = curr[folder]
                        curr.setTitle(folder)
                        curr.reindexObject()

                content_type = mimetypes.guess_type(file_name)[0] or ""
                self.factory(file_name, content_type, stream, curr, force_files)

                plone.api.portal.show_message(_(u'Zip file imported'), self.request, type="info")
        self.request.response.redirect(self.context.absolute_url())

    def factory(self, name, content_type, data, container, force_files):
        ctr = plone.api.portal.get_tool('content_type_registry')
        type_ = ctr.findTypeName(name.lower(), content_type, '')
        if force_files and type_ not in ('File', 'Image'):
            type_ = 'File'
        elif not type_:
            type_ = 'File'

        normalizer = getUtility(IFileNameNormalizer)
        chooser = INameChooser(self.context)
        newid = chooser.chooseName(normalizer.normalize(name), self.context.aq_parent)

        obj = plone.api.content.create(container=container, type=type_, id=newid, title=name)
        primary_field = IPrimaryFieldInfo(obj)
        if isinstance(primary_field.field, RichText):
            setattr(obj, primary_field.fieldname, RichTextValue(data))
        else:
            setattr(obj, primary_field.fieldname, primary_field.field._type(data, filename=utils.safe_unicode(name)))
        obj.reindexObject()
