import ims.zip
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import PloneSandboxLayer, IntegrationTesting, FunctionalTesting, applyProfile


class ZipSiteLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configuration_context):
        self.loadZCML(package=ims.zip)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ims.zip:default')


ZIP_SITE_FIXTURE = ZipSiteLayer()

INTEGRATION = IntegrationTesting(
    bases=(ZIP_SITE_FIXTURE,),
    name="ims.zip:Integration"
)

FUNCTIONAL = FunctionalTesting(
    bases=(ZIP_SITE_FIXTURE,),
    name="ims.zip:Functional"
)
