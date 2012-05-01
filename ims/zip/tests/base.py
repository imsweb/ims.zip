# -*- coding: utf-8 -*-
#
# File: base.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__ = 'Ramon Bartl <ramon.bartl@inquant.de>'
__docformat__ = 'plaintext'


from Zope2.App import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_product():
    """Set up additional products and ZCML required to test this product.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    fiveconfigure.debug_mode = True
    import ims.zip
    zcml.load_config('configure.zcml', ims.zip)
    fiveconfigure.debug_mode = False

    ztc.installPackage('ims.zip')

setup_product()
ptc.setupPloneSite(products=['ims.zip'])


class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    def afterSetUp(self):
      self.setRoles(["Manager"])
      self.cat = self.portal.portal_catalog
      self.folder1_id = 'folder1'
      self.folder2_id = 'folder2'
      self.folder3_id = 'folder3'
      
    def _createStructure(self):
      """ /folder1
          /folder2/folder3 """
      self.portal.invokeFactory("Folder", id=self.folder1_id)
      self.folder1 = self.portal[self.folder1_id]
      self.portal.invokeFactory("Folder", id=self.folder2_id)
      self.folder2 = self.portal[self.folder2_id]
      self.portal.folder2.invokeFactory("Folder", id=self.folder3_id)
      self.folder3 = self.portal.folder2[self.folder3_id]

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """