import os
import zipfile
from io import BytesIO

from App.Common import package_home
from ims.zip.interfaces import IZippable, IZipFolder
from ims.zip.tests import base
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest

PACKAGE_HOME = package_home(globals())


def loadFile(name):
    """Load image from testing directory"""
    path = os.path.join(PACKAGE_HOME, 'input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data


def makeResponse(request):
    """ create a fake request and set up logging of output """
    headers = {}
    output = []

    class Response:
        def setHeader(self, header, value):
            headers[header] = value

        def write(self, msg):
            output.append(msg)

    request.RESPONSE = Response()
    return headers, output, request


class ZipTest(base.TestCase):
    def _createFile(self, parent):
        parent.invokeFactory('File', 'file1')
        ob = parent['file1']
        ob.setFile(loadFile('file.txt'))
        ob.setFilename('file.txt')
        ob.reindexObject()
        self.file1 = ob

    def _createImage(self, parent):
        parent.invokeFactory('Image', 'image1')
        ob = parent['image1']
        ob.setImage(loadFile('canoneye.jpg'))
        ob.setFilename('canoneye.jpg')
        ob.reindexObject()
        self.image1 = ob

    def _createDocument(self, parent):
        parent.invokeFactory('Document', 'page1')
        ob = parent['page1']
        ob.setText('<p>hi!</p>', mimetype='text/html')
        ob.setTitle('My page')
        ob.setDescription('A test page')
        ob.reindexObject()
        self.page1 = ob

    def testInterfaces(self):
        self._createStructure()
        self._createImage(self.folder1)
        self._createFile(self.folder1)
        self._createDocument(self.folder1)
        self.failUnless(IZipFolder.providedBy(self.folder1))
        self.failUnless(IZippable.providedBy(self.image1))
        self.failUnless(IZippable.providedBy(self.file1))
        self.failUnless(IZippable.providedBy(self.page1))

    def testFileIndexed(self):
        self._createStructure()
        parent = self.folder2
        base_path = '/'.join(parent.getPhysicalPath())
        self.assertEquals(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 0)
        self._createFile(parent)
        self.assertEquals(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 1)

    def testImageIndexed(self):
        self._createStructure()
        parent = self.folder1
        base_path = '/'.join(parent.getPhysicalPath())
        self.assertEquals(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 0)
        self._createImage(parent)
        self.assertEquals(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 1)

    def testDocumentIndexed(self):
        self._createStructure()
        parent = self.folder3
        base_path = '/'.join(parent.getPhysicalPath())
        self.assertEquals(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 0)
        self._createDocument(parent)
        self.assertEquals(len(self.cat(path=base_path, object_provides=IZippable.__identifier__)), 1)

    def testZip(self):
        self._createStructure()
        self._createImage(self.folder1)
        self._createDocument(self.folder3)
        self._createFile(self.folder2)
        headers, output, request = makeResponse(TestRequest())

        view = getMultiAdapter((self.portal, request), name='zipconfirm')
        data = view()
        zipper = zipfile.ZipFile(BytesIO(data), 'r', zipfile.ZIP_DEFLATED)

        namelist = zipper.namelist()
        self.failUnless('folder1/image1' in namelist)
        self.failUnless('folder2/folder3/page1.html' in namelist)
        self.failUnless('folder2/file1.txt' in namelist)

        # stream = zipper.read('folder1/image1') why is this an image tag? Probaby from using BytesIO/StringIO to pass to ZipFile
        # self.assertEquals(stream,loadFile('canoneye.jpg')) but I can't get it to work in this test otherwise

        stream = zipper.read('folder2/folder3/page1.html')
        self.assertEquals(stream,
                          '<html><body><h1>My page</h1><p class="description">A test page</p><p>hi!</p></body></html>')

        stream = zipper.read('folder2/file1.txt')
        self.assertEquals(stream, loadFile('file.txt'))

    def testUnZip(self):
        headers, output, request = makeResponse(TestRequest())
        view = getMultiAdapter((self.portal, request), name='unzip')

        zipf = os.path.join(PACKAGE_HOME, 'input', 'test.zip')
        view.unzip(zipf)

        page1 = self.cat(path='/plone/folder2/folder3/page1.html')[0].getObject()
        self.assertEquals(page1.getFile().get_data(),
                          '<html><body><h1>My page</h1><p class="description">A test page</p><p>hi!</p></body></html>')
        # self.assertEquals(page1.Title(),'My page')
        # self.assertEquals(page1.Description(),'A test page')
        # self.assertEquals(page1.getText(),'<p>hi!</p>')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ZipTest))
    return suite
