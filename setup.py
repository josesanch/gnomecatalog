#! /usr/bin/env python

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.clean import clean
from distutils.dep_util import newer
from distutils.log import info
import glob
import os
import sys

mod_list = ["gnomecatalog"]

name = "gnomecatalog"
version="0.3.4"
long_desc = '''Catalog Software'''

class CleanData(clean):

	def run(self):

		top =  os.path.join('build', 'mo')
		if os.path.exists(top):
			for root, dirs, files in os.walk(top, topdown=False):
				for name in files:
					os.remove(os.path.join(root, name))
				for name in dirs:
					os.rmdir(os.path.join(root, name))
			os.removedirs(top)
		clean.run(self)


class InstallData(install_data):
  def run (self):
    self.data_files.extend (self._compile_po_files ())
    install_data.run (self)

  def _compile_po_files (self):
    data_files = []

    # Don't install language files on win32
    if sys.platform == 'win32':
      return data_files

    PO_DIR = 'po'
    for po in glob.glob (os.path.join (PO_DIR,'*.po')):
      lang = os.path.basename(po[:-3])
      mo = os.path.join('build', 'mo', lang, 'gnomecatalog.mo')

      directory = os.path.dirname(mo)
      if not os.path.exists(directory):
        info('creating %s' % directory)
        os.makedirs(directory)

      if newer(po, mo):
        # True if mo doesn't exist
        cmd = 'msgfmt -o %s %s' % (mo, po)
        info('compiling %s -> %s' % (po, mo))
        if os.system(cmd) != 0:
          raise SystemExit('Error while running msgfmt')

        dest = os.path.dirname(os.path.join('share', 'locale', lang, 'LC_MESSAGES', 'gnomecatalog.mo'))
        data_files.append((dest, [mo]))

    return data_files

setup (name        = name,
      version          = version,
      description      = 'Catalog Software for Gnome Desktop',
      long_description = long_desc,
      author           = 'Jose Sanchez Moreno',
      author_email     = 'jose@o2w.es',
      url              = 'http://gnomecatalog.sf.net',
      license          = 'GPL v3',
	  packages         = ['gnomecatalog', "gnomecatalog.ui"],
	  scripts          = ['scripts/gnomecatalog'],
      data_files	   = [('share/gnomecatalog/glade', ["share/glade/dialogs.glade","share/glade/gnomecatalog.glade"]),
			          	 ('share/gnomecatalog/pixmaps', glob.glob('share/pixmaps/*.png')),
			          	 ('share/gnomecatalog/pixmaps', glob.glob('share/pixmaps/*.xpm')),
			          	 ('share/applications', ["share/mime/gnomecatalog.desktop"]),
			          	 ('share/mime/packages', ["share/mime/gnomecatalog.xml"]),
						 ('share/mime-info', ["share/mime/gnomecatalog.mime","share/mime/gnomecatalog.keys" ]),
						 ('share/application-registry', ["share/mime/gnomecatalog.applications"]),
						 ('share/icons/hicolor/48x48/mimetypes', ["share/mime/gnome-mime-application-x-gcatalog.png"]),
				         ('share/man/man1', ['doc/gnomecatalog.1'])
      ],
      cmdclass 		   = {'install_data': InstallData, 'clean': CleanData },
	)
