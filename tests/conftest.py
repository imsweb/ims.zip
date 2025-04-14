import os

import pytest
from plone import api
from plone.app.textfield import RichTextValue
from plone.namedfile.file import NamedBlobFile, NamedBlobImage
from pytest_plone import fixtures_factory

from ims.zip.testing import FUNCTIONAL_TESTING
from ims.zip.testing import INTEGRATION_TESTING

base_path = os.path.dirname(os.path.realpath(__file__))

pytest_plugins = ["pytest_plone"]

globals().update(
    fixtures_factory((
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)


@pytest.fixture
def folders(portal):
    folder1 = api.content.create(container=portal, type="Folder", id="f1")
    folder2 = api.content.create(container=portal, type="Folder", id="f2")
    folder3 = api.content.create(container=folder2, type="Folder", id="f3")
    return folder1, folder2, folder3


@pytest.fixture
def load_zip():
    def load_zip(name):
        with open(os.path.join(base_path, "input", name), "rb") as zipf:
            data = zipf.read()
        return data

    return load_zip


@pytest.fixture
def load_file():
    def load_file(name):
        """Load image from testing directory"""
        path = os.path.join(base_path, "input", name)
        with open(path, "rb") as _file:
            data = _file.read()
        return NamedBlobFile(data)

    return load_file


@pytest.fixture
def load_image():
    def load_image(name):
        """Load image from testing directory"""
        path = os.path.join(base_path, "input", name)
        with open(path, "rb") as _file:
            data = _file.read()
        return NamedBlobImage(data)

    return load_image


@pytest.fixture
def create_file(load_file):
    def create_file(parent):
        ob = api.content.create(container=parent, id="file1", type="File", file=load_file("file.txt"))
        ob.file.filename = "file.txt"
        return ob

    return create_file


@pytest.fixture
def create_image(load_image):
    def create_image(parent):
        ob = api.content.create(container=parent, id="image1", type="Image", image=load_image("canoneye.jpg"))
        ob.image.filename = "canoneye.jpg"
        return ob

    return create_image


@pytest.fixture
def create_document():
    def create_document(parent):
        ob = api.content.create(
            container=parent,
            id="page1",
            type="Document",
            text=RichTextValue("<p>hi!</p>"),
            description="A test page",
            title="My page",
        )
        return ob

    return create_document
