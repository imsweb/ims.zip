import zipfile
from io import BytesIO

from plone import api
from plone.namedfile.file import NamedBlobFile

from ims.zip.interfaces import IZippable, IZipFolder

PAGE_TEXT = (
    b'<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><body><h1>My page</h1>'
    b'<p class="description">A test page</p><p>hi!</p></body></html>'
)


class TestBasic:
    def test_interfaces(self, create_image, create_file, create_document, folders):
        folder1, _folder2, _folder3 = folders
        img = create_image(folder1)
        file_ = create_file(folder1)
        doc = create_document(folder1)
        assert IZipFolder.providedBy(folder1)
        assert IZippable.providedBy(img)
        assert IZippable.providedBy(file_)
        assert IZippable.providedBy(doc)

    def test_file_indexed(self, folders, create_file):
        parent = folders[1]
        base_path = "/".join(parent.getPhysicalPath())
        assert len(api.content.find(path=base_path, object_provides=IZippable.__identifier__)) == 0
        create_file(parent)
        assert len(api.content.find(path=base_path, object_provides=IZippable.__identifier__)) == 1

    def test_image_indexed(self, folders, create_image):
        parent = next(iter(folders))
        base_path = "/".join(parent.getPhysicalPath())
        assert len(api.content.find(path=base_path, object_provides=IZippable.__identifier__)) == 0
        create_image(parent)
        assert len(api.content.find(path=base_path, object_provides=IZippable.__identifier__)) == 1

    def test_document_indexed(self, folders, create_document):
        parent = folders[2]
        base_path = "/".join(parent.getPhysicalPath())
        assert len(api.content.find(path=base_path, object_provides=IZippable.__identifier__)) == 0
        create_document(parent)
        assert len(api.content.find(path=base_path, object_provides=IZippable.__identifier__)) == 1

    def test_zip(self, portal, folders, create_image, create_file, create_document, load_image, load_file):
        folder1, folder2, folder3 = folders
        create_image(folder1)
        create_document(folder3)
        create_file(folder2)

        view = api.content.get_view("zipconfirm", context=portal)
        data = view()
        zipper = zipfile.ZipFile(BytesIO(data), "r", zipfile.ZIP_DEFLATED)

        namelist = zipper.namelist()
        assert "f1/image1.jpg" in namelist
        assert "f2/f3/page1.html" in namelist
        assert "f2/file1.txt" in namelist

        stream = zipper.read("f1/image1.jpg")
        assert stream == load_image("canoneye.jpg").data

        stream = zipper.read("f2/f3/page1.html")
        assert stream == PAGE_TEXT

        stream = zipper.read("f2/file1.txt")
        assert stream == load_file("file.txt").data

    def test_unzip(self, portal, load_zip):
        view = api.content.get_view("unzip", context=portal)

        data = load_zip("test.zip")
        zipf = NamedBlobFile(data=data)
        view.unzip(zipf)

        page1 = next(iter(api.content.find(path="/plone/folder2/folder3/page1.html"))).getObject()
        assert page1.text.raw == PAGE_TEXT
        assert page1.title == "page1.html"
