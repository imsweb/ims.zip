from zope import schema

from plone.namedfile.field import NamedFile
from plone.supermodel import model
from zope.interface.interface import Interface

from . import _


class IZipper(Interface):
    """Zipper utility"""


class IZippable(Interface):
    """Defines what can be zipped"""

    def get_zippable(self):
        """Return the zippable stream of this content"""


class IZipFolder(Interface):
    """Locations where you can zip content"""


class IUnzipForm(model.Schema):
    file = NamedFile(
        title=_("Zip File"),
        required=True,
    )
    force_files = schema.Bool(
        title=_("Force upload as Files"),
        description=_("If unchecked, some files will become Pages, such as .html and .txt"),
        required=False,
    )


class IZipSettings(model.Schema):
    technical_support_address = schema.TextLine(title=_("Technical Support name"))
