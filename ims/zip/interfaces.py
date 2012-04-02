from zope import interface, component
from Products.CMFCore.interfaces import ISiteRoot

class IZipper(interface.Interface):
    """ Zipper utility """

class IZippable(interface.Interface):
    """ Defines what can be zipped """
  
    def getZippable(self):
      """ Return the zippable stream of this content """

class IZipFolder(interface.Interface):
    """ Locations where you can zip content """