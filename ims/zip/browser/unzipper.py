import zipfile, os
from zope import component
from Products.CMFCore.interfaces import ISiteRoot
from StringIO import StringIO
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory

class Unzipper(BrowserView):

  def __init__(self,context,request):
    self.context=context
    self.request=request

  def __call__(self):
    form = self.request.form
    if 'form.submitted' in form:
      zipf = self.request.form.get('file','')
      return self.unzip(zipf)
    return self.index()

  def unzip(self, zipf):
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
      factory = None
      if mimetype and [m for m in mimetype.mimetypes if 'image/' in m]:
        factory = self.createImage
      elif 'text/html' == mimetype:
        factory = self.createDocument
      elif id:
        factory = self.createFile
      if factory:
        factory(curr, id, stream)
      
      self.context.plone_utils.addPortalMessage(PloneMessageFactory(u'Zip file imported'))
    return self.context()
      
  def createFile(self, parent, id, stream):
    parent.invokeFactory('File',id)
    ob=parent[id]
    ob.setFile(stream)
    ob.reindexObject()
      
  def createImage(self, parent, id, stream):
    parent.invokeFactory('Image',id)
    ob=parent[id]
    ob.setImage(stream)
    ob.reindexObject()
      
  def createDocument(self, parent, id, stream):
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