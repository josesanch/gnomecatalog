# -*- coding: UTF-8 -*-
import gtk, gnomevfs, gobject
import tarfile, zipfile
import os, re, pprint
import string, sys
import utils
import fstypes, urllib


class Reader:
	""" Lector de ficheros """

	def __init__(self):
		self._cancel_import_disk = False


	def dir_count(self, uri):
		count = 0
		for info in gnomevfs.DirectoryHandle(uri):
			if info.name == '.' or info.name == '..' or info.name[0] == ".": continue
			if info.type and info.type == 2: count += self.dir_count(uri + "/" + info.name)
			count += 1
		return count


	def read(self, uri, progress = None, recursive = None):
		pos = 0; files = []; dirs = [];
		""" La primera vez que se llama """
		try:
			path = gnomevfs.get_local_path_from_uri(uri)
		except:
			path = uri

		if not recursive:
			self.progress_bar = progress
			self.clear_progress_bar()
			self._cancel_import_disk = False
			self.count_files = 1;	self.position = 0;	self.root = path

			""" Creamos un nuevo disco """
			self.disk = fstypes.Disk(utils.get_label(path), path, None, None, 0, utils.get_drive_icon(str(path)))

			""" Contamos los archivos primero, para luego poder poner el progreso """
			self.count_files = self.dir_count(uri)
			gobject.timeout_add(500, self.update_progress_bar)


		for info in gnomevfs.DirectoryHandle(uri):
			if(self._cancel_import_disk):
				return None

			""" Insertamos el archivo, si no es un archivo oculto """
			if info.name == '.' or info.name == '..' or info.name[0] == ".":
				continue

			self.position += 1

			pathfile = uri + "/" +  urllib.pathname2url(info.name)
			self.path = pathfile
			file = fstypes.File(pathfile, self.disk)
			if info.type and info.type == 2:
				file.add_files(self.read(pathfile, None, True))	# Directory

			files.append(file)

			if not recursive:
				self.disk.add(file)


		if(self._cancel_import_disk):
			return None

		if not recursive:
			self.progress_bar = None
			return self.disk
		else:
			return files


	def update_progress_bar(self):
#		print "update " + str(self.position)
		if not self.progress_bar:
			return 	False

		if self.position > self.count_files:
			self.position = self.count_files

		if self.path:
			self.progress_bar.set_text("  " + _("Importing ") + self.path  + " (" +  str(self.position) + "/" + str(self.count_files) + ")  ")

		self.progress_bar.set_fraction(float(self.position) / float(self.count_files))

		return True

	def clear_progress_bar(self):
		if self.progress_bar:
			self.progress_bar.set_text(_('Importing files ...'))
			self.progress_bar.set_fraction(0)

	def cancel_import_disk(self):
		self.progress_bar = None
		self._cancel_import_disk = True




if __name__ == "__main__":
	reader = Reader()


#	pprint.pprint(reader.read("/home/jose/Desktop"))
	pprint.pprint(reader.read("/home/jose/Desktop/Peliculas"))
#	print reader.read("/home/jose")
