import zipfile
from io import BytesIO
import os
from zope.component import queryAdapter

from .interfaces import IZippable


def zipfiles(content, base_path, zip64=False):
    """Return the path and file stream of all content we find here"""
    fstream = BytesIO()

    zipper = zipfile.ZipFile(fstream, 'w', zipfile.ZIP_DEFLATED, allowZip64=zip64)

    for c in content:
        rel_path = c.getPath().split(base_path)[1:] or [c.getId]  # the latter if the root object has an adapter
        if rel_path:
            obj = c.getObject()
            zip_path = os.path.join(*rel_path)
            adapter = queryAdapter(obj, IZippable)
            stream = adapter.zippable()
            if stream:
                ext = adapter.extension()
                component_name = zip_path + ext
                zipper.writestr(component_name, stream)
                created = obj.created()
                zipper.NameToInfo[component_name].date_time = (
                    created.year(), created.month(), created.day(), created.hour(), created.minute(),
                    int(created.second()))
    zipper.close()
    return fstream.getvalue()
