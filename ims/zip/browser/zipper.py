import zipfile
from email.mime.text import MIMEText

from plone import api
from Products.Five.browser import BrowserView
from plone.namedfile.file import NamedBlobFile

from .. import _
from ..interfaces import IZippable
from ..interfaces import IZipSettings
from ..zipper import zipfiles


def convert_to_bytes(size):
    num, unit = size.split()
    if unit.lower() == "kb":
        return float(num) * 1024
    elif unit.lower() == "mb":
        return float(num) * 1024 * 1024
    elif unit.lower() == "gb":
        return float(num) * 1024 * 1024 * 1024
    else:
        return float(num)


def _get_size(view):
    base_path = "/".join(view.context.getPhysicalPath()) + "/"  # the path in the ZCatalog

    content = api.content.find(path=base_path, object_provides=IZippable.__identifier__)
    return sum([(b.getObjSize and convert_to_bytes(b.getObjSize)) or 0 for b in content])


def _is_small_zip(view):
    return _get_size(view) <= 4 * 1024.0 * 1024.0 * 1024.0  # 4 GB


class ZipPrompt(BrowserView):
    """confirm zip"""

    def technical_support_address(self):
        return api.portal.get_registry_record("ims.zip.interfaces.IZipSettings.technical_support_address")

    def get_size(self):
        return _get_size(self)

    def small_zip(self):
        return _is_small_zip(self)

    def size_estimate(self):
        return "%.2f MB" % (_get_size(self) / 1024.0 / 1024)


class Zipper(BrowserView):
    """Zips content to a temp file"""

    def technical_support_address(self):
        return api.portal.get_registry_record(
            name="technical_support_address", interface=IZipSettings
        ) or api.portal.get_registry_record("plone.email_from_address")

    def __call__(self):
        try:
            return self.do_zip()
        except zipfile.LargeZipFile:
            message = _("This folder is too large to be zipped. Try zipping subfolders individually.")
            api.portal.show_message(message, self.request, type="error")
            return self.request.response.redirect(self.context.absolute_url())

    def do_zip(self):
        """Zip all of the content in this location (context)"""
        if not _is_small_zip(self):
            # force this, whether it was passed in the request or not
            self.request["zip64"] = 1

        base_path = "/".join(self.context.getPhysicalPath()) + "/"  # the path in the ZCatalog

        content = api.content.find(path=base_path, object_provides=IZippable.__identifier__)
        if not self.request.get("zip64"):
            self.request.response.setHeader("Content-Type", "application/zip")
            self.request.response.setHeader("Content-disposition", f"attachment;filename={self.context.getId()}.zip")
            return zipfiles(content, base_path)
        else:
            fstream = zipfiles(content, base_path, zip64=True)
            obj_id = f"{self.context.getId()}.zip"
            container = api.portal.get()
            if obj_id not in container:
                obj = api.content.create(
                    type="File", id=obj_id, container=container, file=NamedBlobFile(fstream, filename=obj_id)
                )
            else:
                obj = container[obj_id].file = NamedBlobFile(fstream, filename=obj_id)

            msg = f'<p>Your zip file is ready for download at <a href="{obj.absolute_url()}/view">{obj.title}</a>'
            mail = api.portal.get_tool("MailHost")
            site_from = api.portal.get_registry_record("plone.email_from_address")
            portal_title = api.portal.get_registry_record("plone.site_title")
            mail.send(
                MIMEText(msg, "html"),
                mto=api.user.get_current().getProperty("email"),
                mfrom=site_from,
                subject=f"Zip file ready at {portal_title}",
            )
