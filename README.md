# ims.zip

ims.zip is a package for zipping and unzipping content on a Plone site. The zipping and
unzipping process is not lossless; only minimal metadata is maintained on zipping and in some
cases the content type may change (Pages are zipped as HTML files, but HTML files are
unzipped as Files).

Folder structure is maintained on both zip and unzip.

## Unzipping

Unzipping is fairly straight forward. We attempt to find the appropriate content type

## Interfaces

There are two important interfaces used for zipping and unzipping. Implementing these interfaces means the following:

* IZipFolder - a container object that has Actions for zipping and unzipping. By
default this is provided by Dexterity containers
* IZippable - the object can be zipped. An adapter determines how the file will be rendered inside the zip file

## Adapters

Adapters can *provide* the IZippable interface which tells the zip utility how to create
a file and what extension it should have. Adapters should implement the following
methods:
* zippable - data stream
* extension - the file extension

Custom content types can provide adapters for objects that implement IZippable.

### Included Adapters

This package already contains adapters for common Dexterity types.
* File
* Image
* Document (saves as HTML file)

