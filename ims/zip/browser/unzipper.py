import zipfile, os
from zope import component
from Products.CMFCore.interfaces import ISiteRoot
from StringIO import StringIO
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from zope.filerepresentation.interfaces import IFileFactory
import mimetypes

class Unzipper(BrowserView):

  def __init__(self,context,request):
    self.context=context
    self.request=request

  def __call__(self):
    form = self.request.form
    if 'form.submitted' in form:
      zipf = self.request.form.get('file','')
      force_files = self.request.form.get('force_files',False)
      return self.unzip(zipf,force_files)
    return self.index()

  def unzip(self, zipf, force_files=False):
    portal = component.getUtility(ISiteRoot)
    mimereg = getToolByName(portal,'mimetypes_registry')
    zipper = zipfile.ZipFile(zipf, 'r')

    for name in zipper.namelist():
      path,id = os.path.split(name)
      stream = zipper.read(name)
      curr = self.context
      for folder in [f for f in path.split('/') if f]:
        try:
          curr = curr[folder]
        except KeyError:
          curr.invokeFactory('Folder',folder)
          curr = curr[folder]
          curr.setTitle(folder)
          curr.reindexObject()
      mimetype = mimereg.lookupExtension(id)
      
      if 'text/html' == mimetype and not force_files:
        self.createDocument(curr, id, stream, mimetype)
      elif not force_files:
        content_type = mimetypes.guess_type(id)[0] or ""
        factory = IFileFactory(self.context)
        f = factory(id, content_type, stream)
      else:
        self.createFile(curr, id, stream, mimetype)
      
      self.context.plone_utils.addPortalMessage(PloneMessageFactory(u'Zip file imported'))
    return self.context()
      
  def createFile(self, parent, id, stream, mimetype):
    parent.invokeFactory('File',id)
    ob=parent[id]
    ob.setTitle(id)
    ob.setFile(stream)
    ob.setFilename(id)
    ob.setFormat(mimetype)
    ob.reindexObject()
      
  def createDocument(self, parent, id, stream, mimetype):
    id = '.' in id and '.'.join(id.split('.')[:-1]) or id
    from elementtree import ElementTree as et
    tree = et.parse(StringIO(stream))
    
    body = tree.find('body')
    title = body.findtext('h1')
    if title:
      body.remove(body.find('h1'))
    desc = ''
    p = body.find('p')
    if p.attrib['class'] == 'description':
      desc = p.text
      body.remove(p)

    out = StringIO()
    tree.write(out)
    text = out.getvalue()

    parent.invokeFactory('Document',id)
    ob=parent[id]
    ob.setText(text,mimetype="text/html")
    ob.setTitle(title)
    ob.setDescription(desc)
    ob.reindexObject()