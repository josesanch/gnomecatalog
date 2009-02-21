# -*- coding: UTF-8 -*-
import gtk, os.path
import fileinfo, utils, config, thumbnails
config = config.Config()
thumbnails = thumbnails.Thumb(config.get('database'))
icon_size = w = h = 24
icon_theme = gtk.icon_theme_get_default()

icons = {
					"directory" : icon_theme.load_icon("folder", icon_size, 0),
					"audio": icon_theme.load_icon("audio-x-generic", icon_size, 0),
					"video": icon_theme.load_icon("video-x-generic", icon_size, 0),
					"image": icon_theme.load_icon("image-x-generic", icon_size, 0),
					"package": icon_theme.load_icon("gnome-package", icon_size, 0),
					"default": icon_theme.load_icon("document", icon_size, 0),
					"loading": icon_theme.load_icon("gnome-fs-loading-icon", icon_size, 0),
					"catalog": icon_theme.load_icon("folder", icon_size, 0),
					"cdrom": icon_theme.load_icon("media-optical", icon_size, 0),
		}



class FstypeBase:
	model_disk = None
	model_files = None

	def __init__(self):
		self._data_loaded = False
		self.db = self.id = self.name = self.comment = None
		self.items = []
		self.size = None
		self.rating = None
		self._index = 0
		self._count = 0
		self.iter = None
		self.metadata = None
		self.path = None
		self.type = None


	def is_catalog(self): return False
	def is_disk(self): return False
	def is_file(self): return False
	def is_dir(self): return False

	def __iter__(self):
		if not self._data_loaded:
			self.items = self._load_data()
			self._data_loaded = True

		self._count = len(self.items)
		self._index = 0
		return self

	def next(self):
		if self._index >= self._count: raise StopIteration
		self._index = self._index + 1
		return self.items[self._index - 1]

	def _load_data(self): pass



class Catalog(FstypeBase):
	def __init__(self, name, id = None, db = None,  idcatalog = 0, comment = None, borrow = None):
		FstypeBase.__init__(self)
		self.iter = None
		self.catalog = None
		self.name = name
		self.db = db
		self.idcatalog = idcatalog
		self.comment = comment
		self.borrow = borrow
		self.id = id

	def add(self, item):
		self.items.append(item)

	def is_catalog(self): return True

	def get_icon(self): return icons["catalog"]

	def _load_data(self):
		if self.db:
			return self.db.read_data(self.id)
		else:
			return []


	def __setattr__(self, name, value):
		if name in ["name", "idcatalog", "comment", "borrow"]:
			if self.id and self.__dict__[name] != value:
				self.__dict__[name] = value
				self.db.update("catalogs", self.id, name, value)
				if self.__dict__.has_key('iter') and self.iter != None:
					FstypeBase.model_disk.set_value(self.iter, 1, self.get_text())
			else:
				self.__dict__[name] = value
		else:
			self.__dict__[name] = value


	def get_text(self):
		txt = self.name
		if self.comment:
			txt  = txt + "\n<span foreground='#e0e0e0'><small>" + self.comment + "</small></span>";

		if self.borrow:
			txt  = txt  + "\n<span foreground='#ff1010'><small>" + _("Borrowed to ") + self.borrow + "</small></span>";
		return txt


	def delete(self):
		for i in self.items:
			i.delete()
		self.db.delete("catalogs", self.id)
		self.db.commit()

	def get_catalog(self):
		if self.catalog: return self.catalog
		if self.idcatalog:
			d = self.db.get_catalog(self.idcatalog)[0]
			self.catalog = Catalog(d["name"], d["id"], self.db, d["idcatalog"])
			return self.catalog



class Disk(FstypeBase):

	def __init__(self, name,  path, id = None, db = None, idcatalog = 0, icon = None, comment = None, borrow = None):
		FstypeBase.__init__(self)
		self.iter = None
		self.catalog = None
		self.name = name
		self.path = path
		self.db = db
		self.idcatalog = idcatalog
		self.icon = None
		self.comment = comment
		self.borrow = borrow
		self.id = id
		""" Desde la bd """
		if type(icon) == gtk.gdk.Pixbuf:
			self.icon = icon

		if type(icon) == buffer:
			open('/tmp/tmp_gnomecatalog_icon.png', 'wb').write(icon)
			self.icon =  gtk.gdk.pixbuf_new_from_file_at_size("/tmp/tmp_gnomecatalog_icon.png", 24, 24)

		if not db:
			self._data_loaded = True

	def add(self, file):
		self.items.append(file)

	def is_disk(self): return True

	def get_icon(self):
		if self.icon:
			return self.icon

		return icons["cdrom"]

	def __setattr__(self, name, value):
		if name in ["name", "idcatalog", "comment", "borrow"]:
			if self.id and self.__dict__[name] != value:
				self.__dict__[name] = value
				self.db.update("disks", self.id, name, value)
				if self.__dict__.has_key('iter') and self.iter != None:
					FstypeBase.model_disk.set_value(self.iter, 1, self.get_text())
			else:
				self.__dict__[name] = value
		else:
			self.__dict__[name] = value



	def get_text(self):
		txt = self.name
		if self.comment:
			txt  = txt + "\n<span foreground='#e0e0e0'><small>" + self.comment + "</small></span>";
		if self.borrow:
			txt  = txt  + "\n<span foreground='#ff1010'><small>" + _("Borrowed to ") + self.borrow + "</small></span>";
		return txt


	def _load_data(self):
		return self.db.read_files_from_disk(self)

	def delete(self):
#		for i in self.items:
#			i.delete()
#		print "Eliminando",self.id
		self.db.remove_disk(self.id)
		self.db.commit()


	def get_catalog(self):
		if self.catalog: return self.catalog
		if self.idcatalog:
			d = self.db.get_catalog(self.idcatalog)[0]
			self.catalog = Catalog(d["name"], d["id"], self.db, d["idcatalog"])
			return self.catalog



class File(FstypeBase):

	""" Acepta como informacion de bd o path """
	def __init__(self, info = None, disk = None, db = None):
		FstypeBase.__init__(self)
		self.__categories = None
		self.iter = None
		self.disk = disk
		self.path = None
		self.duration = None

		if type(info) == str:
			self._data_loaded = True
			finfo = fileinfo.Info()
			self.path , self.name, self.size, self.type, self.mime, self.meta = finfo.get(info)


		if type(info) == dict:
			self.name = info["name"]
			self.comment = info["comment"]
			self.rating = info["rating"]
			self.path = info["path"]
			self.size = info["size"]
			self.type = info["type"]
			self.mime = info["mime"]
			self.iddisk = info["iddisk"]
			self.db	 = db
			self.id   = info["id"]

	def get_text(self):
		return self.name

	def get_icon(self, size = 24):
		if self.is_dir(): return icons["directory"]
		if not self.mime: return icons['default']
		type, subtype = self.mime.split("/")
		thumb = thumbnails.get_pixbuf(self.id)
		if thumb:
			return thumb

		if size == w and icons.has_key(self.mime):
			return icons[self.mime]

		try:
			icon = icon_theme.load_icon("gnome-mime-" + type + "-" + subtype, size, 0)
			if size == w: icons[self.mime] = icon
			return icon
		except:
			if icons.has_key(type): return icons[type]

		return icons["default"]


	def is_dir(self):
		return self.type == "directory"
		# or self.mime == "application/x-compressed-tar"


	def is_file(self):
		return self.type == "regular"

	def add_files(self, files):
		self.items = files

	def __setattr__(self, name, value):
		if name in ["name", "comment", "rating"] and self.db and self.id != None and self.__dict__[name] != value:
			self.db.update("files", self.id, name, value)
		self.__dict__[name] = value


	def get_disk(self):
		if self.disk: return self.disk
		if self.iddisk:
			d = self.db.get_disk(self.iddisk)[0]
			self.disk = Disk( d["name"], d["root"], d["id"], self.db, d["idcatalog"])
			return self.disk


	def _load_data(self):
		return self.db.read_files_from_disk(self.disk, self.id)


	def delete(self):
		for i in self.items:
			i.delete()
		self.db.delete("files", self.id)

	def get_location(self):
		disk = self.get_disk()
		item = disk
		txt = ""
		while True:
		   item = item.get_catalog()
		   if not item: break
		   txt = txt + item.name + " / "
		txt = txt + disk.name

		dir = os.path.dirname(self.path)[len(disk.path) + len("file:///")-1:]

		if dir: txt = txt + " - " + dir
		return txt


	def get_categories(self):
		if self.__categories:
			return self.__categories
		if self.id:
			self.__categories = self.db.get_categories_from_file(self.id)
		return self.__categories


	def get_metadata(self):
		if self.id and self.metadata == None:
			self.metadata = self.db.get_metadata_from_file(self.id)
#			print self.metadata
		return self.metadata

	def get_duration(self):
		if self.duration == None:
			self.duration = self.db.get_duration(self.id)

		return self.duration

	def get_duration_backup(self):
		metadata = self.get_metadata()
		if not metadata: return None
		if metadata.has_key("length"): return metadata["length"]
		if metadata.has_key("LENGTH"): return metadata["LENGTH"]
		if metadata.has_key("duration"):
				return int(metadata["duration"])   / (1000 * 1000 * 1000)
		return None
