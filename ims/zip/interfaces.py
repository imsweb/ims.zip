from zope.interface import Interface

class IZipper(Interface):
    """ Zipper utility """

class IZippable(Interface):
    """ Defines what can be zipped """
  
    def getZippable(self):
      """ Return the zippable stream of this content """

class IZipFolder(Interface):
    """ Locations where you can zip content """