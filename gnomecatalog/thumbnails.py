# -*- coding: UTF-8 -*-

import gtk, gtk.glade, gconf, gnomevfs, os, string, commands, md5, sys, urllib, shutil
class Thumb:
	size = 64
	def __init__(self, database):
		self.conf_client = gconf.client_get_default()
		self.thumbnailers = {}
		self.database = database
		self.thumbnails_dir = database + "_thumbs"

	def get_pixbuf(self, idfile):
		if self.exists(idfile):
			return gtk.gdk.pixbuf_new_from_file_at_size(self.get_path(idfile), self.size, self.size)

	def save(self, idfile, file):
		try:
			type, subtype = string.split(file.mime, "/")
		except:
			return
		if type == "audio" or subtype == "ogg": return

		# Ya está creada
		if self.exists(idfile):
			return

		else:
			self.__generate(idfile, file)

	def get_dir(self):
		return self.thumbnails_dir

	def delete(self, idfile):
		try:
			os.unlink(self.get_path(idfile))
		except:
			pass

	def exists(self, idfile):
		return os.path.exists(self.get_path(idfile))

	def get_path(self, idfile):
		return os.path.join(self.thumbnails_dir, str(idfile) + '.png')

	def __md5(self, path):
		return os.path.join(self.thumbnails_dir, md5.new(str(path)).hexdigest() + ".png")

	def __md5gnome(self, path):
		return os.environ['HOME'] + "/.thumbnails/normal/" + md5.new(str(path)).hexdigest() + ".png"

	""" Genera un nuevo thumb para el fichero """
	def __generate(self, idfile, file):
		type, subtype = string.split(file.mime, "/")

		# Si existe en gnome ya lo copiamos
		if os.path.exists(self.__md5gnome(file.path)):
			gtk.gdk.pixbuf_new_from_file_at_size(self.__md5gnome(file.path), self.size, self.size).save(self.get_path(idfile), 'png')
#			shutil.copyfile(self.__md5gnome(path), self.__md5(path))

		else:
			if type == "image":
				try:
					image = urllib.url2pathname(str(file.path))[7:]
					dest = self.get_path(idfile)
					gtk.gdk.pixbuf_new_from_file_at_size(image, self.size, self.size).save(dest, 'png')
				except:
					return None

			else:
				thumbnailer = self.__get_thumbnailers(file, type + "@" + subtype, idfile)
				if thumbnailer != None:
					output = commands.getoutput(thumbnailer)


	def __get_thumbnailers(self, file, mime, idfile):
		if self.thumbnailers.has_key(mime):
			thumbnailer = self.thumbnailers[mime]
		else:
			try:
				thumbnailer = self.conf_client.get_string("/desktop/gnome/thumbnailers/" + mime + "/command")
			except:
				return None

		self.thumbnailers[mime] = thumbnailer

		if thumbnailer == None or thumbnailer == "": return None
		thumbnailer = string.replace(thumbnailer, "%s", str(self.size))
		thumbnailer = string.replace(thumbnailer, "%u", '"' + str(file.path) + '"')
		thumbnailer = string.replace(thumbnailer, "%o", '"' + self.get_path(idfile) + '"')
#		print thumbnailer
		return thumbnailer

	def save_from_file(self, idfile, path):
		gtk.gdk.pixbuf_new_from_file_at_size(path, self.size, self.size).save(self.get_path(idfile), 'png')

if __name__ == "__main__":
	t = Thumb()
#	t.stat("test.jpg")

#	print t.get_path(sys.argv[1]);
