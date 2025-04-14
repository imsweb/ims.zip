from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing.zope import WSGI_SERVER_FIXTURE
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import ims.zip


class ZipperLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configuration_context):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        self.loadZCML(package=ims.zip)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "ims.zip:default")
        setRoles(portal, TEST_USER_ID, ["Manager"])


FIXTURE = ZipperLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="ZipperLayer:IntegrationTesting",
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="ZipperLayer:FunctionalTesting",
)

RESTAPI_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="ZipperLayer:RestAPITesting",
)

ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="ZipperLayer:AcceptanceTesting",
)
