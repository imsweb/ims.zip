import unittest

import plone.api as api
import transaction
from ims.zip import testing
from plone.app.testing import setRoles, TEST_USER_ID, SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.zope import Browser


class UnitTestCase(unittest.TestCase):
    def setUp(self):
        pass


class IntegrationTestCase(unittest.TestCase):
    layer = testing.INTEGRATION

    def setUp(self):
        super().setUp()
        self.portal = self.layer['portal']
        self.request = self.layer
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.folder1 = api.content.create(container=self.portal, type='Folder', id='f1')
        self.folder2 = api.content.create(container=self.portal, type='Folder', id='f2')
        self.folder3 = api.content.create(container=self.folder2, type='Folder', id='f3')
        self.cat = api.portal.get_tool('portal_catalog')


class FunctionalTestCase(IntegrationTestCase):
    layer = testing.FUNCTIONAL

    def setUp(self):
        super().setUp()
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )
        transaction.commit()
