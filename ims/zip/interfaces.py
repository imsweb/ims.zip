from plone.directives import form
from plone.namedfile.field import NamedFile
from zope.interface import Interface

from ims.zip import _

class IZipper(Interface):
    """ Zipper utility """

class IZippable(Interface):
    """ Defines what can be zipped """

    def getZippable(self):
      """ Return the zippable stream of this content """

class IZipFolder(Interface):
    """ Locations where you can zip content """

class IUnzipForm(form.Schema):
    file = NamedFile(
              title=_(u"Zip File"),
              required = False,
          )