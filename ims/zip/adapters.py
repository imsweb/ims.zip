from plone.rfc822.interfaces import IPrimaryFieldInfo


class AdapterBase:
    """provide __init__"""

    def __init__(self, context):
        self.context = context

    def extension(self):
        return ""

    def zippable(self):
        return ""


class FileZip(AdapterBase):
    """for File type"""

    def zippable(self):
        primary_field = IPrimaryFieldInfo(self.context)
        return primary_field.value.data

    def extension(self):
        content_id = self.context.getId()
        primary_field = IPrimaryFieldInfo(self.context)
        fn = primary_field.value.filename or content_id
        return (content_id.split(".")[-1] != fn.split(".")[-1] and "." + fn.split(".")[-1]) or ""


class ImageZip(FileZip):
    """for Image type"""


class DocumentZip(AdapterBase):
    """for Document type"""

    def zippable(self):
        template = (
            '<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
            "<body>{header}{description}{text}</body></html>"
        )

        header = f"<h1>{self.context.title}</h1>" if self.context.title else ""
        description = f'<p class="description">{self.context.description}</p>' if self.context.description else ""
        text = ""
        if self.context.text:
            text = self.context.text.raw

        html = template.format(header=header, description=description, text=text)
        return html

    def extension(self):
        return ".html"
