import pytest


class TestUninstall:
    @pytest.fixture(autouse=True)
    def uninstalled(self, installer):
        installer.uninstall_product("ims.zip")

    def test_product_uninstalled(self, installer):
        """Test if ims.zip is cleanly uninstalled."""
        assert installer.is_product_installed("ims.zip") is False
