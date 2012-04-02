from Products.CMFCore.permissions import setDefaultRoles

CanZip='ims.zip: can zip'
setDefaultRoles(CanZip,('Manager',))