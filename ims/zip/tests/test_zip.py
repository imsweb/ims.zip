import os
import zipfile
from io import BytesIO

import plone.api as api
from App.Common import package_home
from ims.zip.interfaces import IZippable, IZipFolder
from plone.app.textfield import RichTextValue
from plone.namedfile.file import NamedBlobFile, NamedBlobImage

from . import base

PACKAGE_HOME = package_home(globals())

PAGE_TEXT = b'<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><body><h1>My page</h1>' \
            b'<p class="description">A test page</p><p>hi!</p></body></html>'


def load_file(name):
    """Load image from testing directory"""
    path = os.path.join(PACKAGE_HOME, 'input', name)
    with open(path, 'rb') as _file:
        data = _file.read()
    return NamedBlobFile(data)


def load_image(name):
    """Load image from testing directory"""
    path = os.path.join(PACKAGE_HOME, 'input', name)
    with open(path, 'rb') as _file:
        data = _file.read()
    return NamedBlobImage(data)


class TestBasic(base.IntegrationTestCase):
    def create_file(self, parent):
        ob = api.content.create(container=parent, id='file1', type='File', file=load_file('file.txt'))
        ob.file.filename = 'file.txt'
        self.file1 = ob
        return ob

    def create_image(self, parent):
        ob = api.content.create(container=parent, id='image1', type='Image', image=load_image('canoneye.jpg'))
        ob.image.filename = 'canoneye.jpg'
        self.image1 = ob
        return ob

    def create_document(self, parent):
        ob = api.content.create(container=parent, id='page1', type='Document', text=RichTextValue('<p>hi!</p>'),
                                description='A test page', title='My page')
        self.page1 = ob
        return ob

    def test_interfaces(self):
        self.create_image(self.folder1)
        self.create_file(self.folder1)
        self.create_document(self.folder1)
        self.assertTrue(IZipFolder.providedBy(self.folder1))
        self.assertTrue(IZippable.providedBy(self.image1))
        self.assertTrue(IZippable.providedBy(self.file1))
        self.assertTrue(IZippable.providedBy(self.page1))

    def test_file_indexed(self):
        parent = self.folder2
        base_path = '/'.join(parent.getPhysicalPath())
        self.assertEqual(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 0)
        self.create_file(parent)
        self.assertEqual(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 1)

    def test_image_indexed(self):
        parent = self.folder1
        base_path = '/'.join(parent.getPhysicalPath())
        self.assertEqual(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 0)
        self.create_image(parent)
        self.assertEqual(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 1)

    def testDocumentIndexed(self):
        parent = self.folder3
        base_path = '/'.join(parent.getPhysicalPath())
        self.assertEqual(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 0)
        self.create_document(parent)
        self.assertEqual(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 1)

    def test_zip(self):
        self.create_image(self.folder1)
        self.create_document(self.folder3)
        self.create_file(self.folder2)

        view = self.portal.restrictedTraverse('zipconfirm')
        data = view()
        zipper = zipfile.ZipFile(BytesIO(data), 'r', zipfile.ZIP_DEFLATED)

        namelist = zipper.namelist()
        self.assertIn('f1/image1.jpg', namelist)
        self.assertIn('f2/f3/page1.html', namelist)
        self.assertIn('f2/file1.txt', namelist)

        stream = zipper.read('f1/image1.jpg')
        self.assertEqual(stream, load_image('canoneye.jpg').data)

        stream = zipper.read('f2/f3/page1.html')
        self.assertEqual(stream, PAGE_TEXT)

        stream = zipper.read('f2/file1.txt')
        self.assertEqual(stream, load_file('file.txt').data)

    def test_unzip(self):
        view = self.portal.restrictedTraverse('unzip')

        with open(os.path.join(PACKAGE_HOME, 'input', 'test.zip'), 'rb') as zipf:
            data = zipf.read()
        zipf = NamedBlobFile(data=data)
        view.unzip(zipf)

        page1 = self.cat(path='/plone/folder2/folder3/page1.html')[0].getObject()
        self.assertEqual(page1.text.raw, PAGE_TEXT)
        self.assertEqual(page1.title, 'page1.html')


def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
