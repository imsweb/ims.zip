from Products.CMFCore.permissions import setDefaultRoles

CanZip = "ims.zip: can zip"
setDefaultRoles(CanZip, ("Manager",))
CanZip = "ims.zip: can unzip"
setDefaultRoles(CanZip, ("Manager",))
