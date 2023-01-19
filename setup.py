from setuptools import setup, find_packages

version = '5.0'

setup(name='ims.zip',
      version=version,
      description="zip and unzip folder contents",
      classifiers=[
          "Framework :: Plone :: 6.0",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3"
      ],
      keywords='',
      author='Eric Wohnlich',
      author_email='wohnlice@imsweb.com',
      url='https://git.imsweb.com/plone/ims.zip',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ims'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      extras_require={
            'test': ['plone.app.testing', 'plone.mocktestcase'],
      },
      )
