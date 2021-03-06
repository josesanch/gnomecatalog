# -*- coding: UTF-8 -*-
import icons, thumbnails
from pysqlite2 import dbapi2 as sqlite
import gtk, time


class ActiveRecord:
	autosave = True
	__columns = []
	data = []

	def __init__(self, *args, **kw):

		self.__columns = self.meta.__dict__.keys()
		self.__columns.remove('__module__')
		self.__columns.remove('__doc__')

		for column in self.__columns:
			self.__dict__[column] = None
		has_to_save = False

		if args:
			if type(args[0]) == dict:
				for item, value in args[0].iteritems():
					self.__dict__[item] = value
				has_to_save = True
		if kw:
			for item, value in kw.iteritems():
				self.__dict__[item] = value
			has_to_save = True

		if (kw.has_key('save') and kw['save'] == True) or not kw.has_key('save'):
			if has_to_save:
				self.save()


	def select(self,  what = None, columns = None, order = None, limit = None):
		if type(what) == int:
			condition = " id = '" + str(what) + "' "
		elif what:
			condition = what
		else:
			condition = None

		if not columns: columns = ", ".join(self.__columns)
		sql = "select " + columns + " from " + self.__TABLE__

		if condition:	sql = sql + " WHERE " + condition
		if order:		sql = sql + " ORDER BY " + order
		if limit:		sql = sql + " LIMIT " + str(limit)

		self.data = self.sql(sql).fetchall()

		if len(self.data) == 0:
			for field in self.__columns:
				self.__dict__[field] = None
		elif len(self.data) == 1:
			for field in self.__columns:
				self.__dict__[field] = self.data[0].__dict__[field]

		return self.data

	def selectFirst(self, what = None):
		return self.select(what, limit = '1')

	def __setattr__(self, name, value):

		if self.autosave and name in self.__columns:
			if self.__dict__[name] != value:
				self.sql("update " + self.__TABLE__ + " SET " + name + " = ? where id = ? ", [value, self.id])
		self.__dict__[name] = value


	def save(self):
		values = []
		columns = []
		for field in self.__columns:
			if self.__dict__[field]:
				values.append(self.__dict__[field])
				if self.id:
					columns.append(field + "=?")
				else:
					columns.append(field)

		if self.id:
 			sql = "UPDATE " + self.__TABLE__ + " SET " + ", ".join(columns) + " WHERE id='" + str(self.id) + "'"
			result = self.sql(sql, values)
		else:
			params = ", ".join(['?'] * len(columns))
			columns = ", ".join(columns)
			sql = "INSERT INTO " + self.__TABLE__ + " (" + columns + ") values (" + params + ")";
			result = self.sql(sql, values)
			self.__dict__['id'] = result.lastrowid


	def delete(self):
		try:
			if self.id:
				self.sql("DELETE FROM " + self.__TABLE__ + " WHERE id= ?", [self.id])
		except:
			pass

	def count(self): pass

	def sql(self, query, params = None):
#		print "SQL: ", query , params
		ActiveRecord.database.set_row_factory(self.row_factory)
		cursor = ActiveRecord.database.get_cursor()
		try:
			if params:
				return cursor.execute(query, params)
			else:
				return cursor.execute(query)
		except:
			print "ERROR ", query, params

	def row_factory(self, cursor, row):
	    d = {}
	    for idx, col in enumerate(cursor.description):
	        d[col[0]] = row[idx]
	    return self.__class__(d, save = False)

	def commit(self):
		ActiveRecord.database.commit()

	def is_catalog(self): return False
	def is_disk(self): return False
	def is_dir(self): return False
	def is_file(self): return False

class Catalogs(ActiveRecord):
	__TABLE__ = 'catalogs'
	class meta:
		id = None
		name = None
		idcatalog = None
		comment = None
		borrow = None

	def is_catalog(self): return True

	def __getattr__(self, key):
		if key == 'catalog':
			if self.idcatalog:
				catalog = Catalogs()
				self.catalog.select('idcatalog=' + str(self.id))
			else:
				self.catalog = None
			return self.catalog

		elif key == 'disks':
			disks = Disks()
			self.disks = disks.select("idcatalog='" + str(self.id) + "'")
			return self.disks
		if self.__dict__.has_key(key):
			return self.__dict__[key]


class Disks(ActiveRecord):
	__TABLE__ = 'disks'
	pixbuf = False
	class meta:
		id = None
		name = None
		volname = None
		root = None
		idcatalog = None
		rating = None
		icon = None
		comment = None
		borrow = None

	def is_disk(self): return True

	def __getattr__(self, key):
		if key == 'files':
			files = Files()
			self.files = files.select('iddisk=' + str(self.id) + ' and (idparent=0 or idparent is null)')
			return self.files

		elif key == 'catalog':
			if self.idcatalog:
				self.catalog = Catalogs()
				self.catalog.select("id = '" + self.idcatalog + "'")
			else:
				self.catalog = None
			return self.catalog

		elif key == 'dirs':
			files = Files()
			self.dirs = files.select('iddisk=' + str(self.id) + " and idparent=0 and type='directory'")
			return self.dirs
		if self.__dict__.has_key(key):
			return self.__dict__[key]



	def get_icon(self):
		if not self.icon: return icons.icons['cdrom']
		if self.pixbuf:
			return self.icon

		open('/tmp/tmp_gnomecatalog_icon.png', 'wb').write(self.icon)
		self.__dict__['icon'] =  gtk.gdk.pixbuf_new_from_file_at_size("/tmp/tmp_gnomecatalog_icon.png", 24, 24)
		self.pixbuf = True
		return self.icon

	def add(self, data):
		if type(data) == list:
			for f in data:
				f.iddisk = self.id
				f.save()
		else:
			data.iddisk = self.id
			data.save()

class Files(ActiveRecord):
	__TABLE__ = 'files'
	class meta:
		id = None
		iddisk = None
		idparent = None
		name = None
		size = None
		date = None
		path = None
		mime = None
		type = None
		comment = None
		rating = None

	def __getattr__(self, key):
		if key == 'files':
			files = Files()
			self.files = files.select('idparent=' + str(self.id))
			return self.files

		elif key == 'disk':
			self.disk = Disks()
			self.disk.select(self.iddisk)
			return self.disk

		elif key == 'metadata':
			metadata = Metadata()
			self.metadata = metadata.select("id='" + str(self.id) + "'")
			return self.metadata

		elif key == 'dirs':
			files = Files()
			self.dirs = files.select('idparent=' + str(self.id) + " and type='directory'")
			return self.dirs

		if self.__dict__.has_key(key):
			return self.__dict__[key]


	def get_icon(self, size = 24):
		if self.icon: return self.icon
		if self.is_dir(): return icons.icons["directory"]
		if not self.mime: return icons.icons['default']

		thumbnail = thumbnails.Thumb("/home/jose/Escritorio/playa.gcatalog")
		thumb = thumbnail.get_pixbuf(self.id)

		if thumb:
			self.__dict__['icon'] = thumb
			return thumb

		if icons.icons.has_key(self.mime):
			return icons.icons[self.mime]

		type, subtype = self.mime.split("/")
		try:
			icon = icons.icon_theme.load_icon("gnome-mime-" + type + "-" + subtype, size, 0)
			icons.icons[self.mime] = icon
			self.__dict__['icon'] = icon
			return icon
		except:
			if icons.icons.has_key(type): return icons.icons[type]

		self.__dict__['icon'] = icons.icons["default"]
		return self.icon

	def is_dir(self):
		return self.type == "directory"
		# or self.mime == "application/x-compressed-tar"

	def is_file(self):
		return not self.is_dir()

	def get_size(self):
		size = self.size
		if not size or size == None or self.is_dir(): return ""
		if size > 1024 * 1024 * 1024:
			return str(round(float(size) / (1024 * 1024 * 1024),2)) + " Gb"
		elif size > 1024 * 1024:
			return str(size / (1024 * 1024)) + " Mb"
		elif size > 1024:
			return str(size / 1024) + " Kb"
		else:
			return str(size) +	"b"

	def get_duration(self):
		if self.duration: return self.duration
		meta = Metadata()
		meta.selectFirst("id = '" + str(self.id)+ "' and (key like 'length' or key='video_length')")
		if meta.value:
			secs = meta.value
			txt = ""
			t = time.localtime(float(secs))
			hour = t[3] - 1
			minute = t[4]
			sec = t[5]
			if hour > 0: txt = txt + str(hour) + "h "
			txt = txt + str(minute) + "m"
			if hour == 0: txt = txt + " " +  str(sec) + "s"
			self.__dict__['duration'] = txt
			return txt

	def search(self, text, categorie = None):
		return self.select("name like '%" + text + "%'")

	def add(self, data):
		if type(data) == list:
			for f in data:
				f.idparent = self.id
				f.iddisk = self.iddisk
				f.save()
		else:
			data.idparent = self.id
			data.iddisk = self.iddisk
			data.save()

class Categories(ActiveRecord):
	__TABLE__ = 'categories'
	class meta:
		id = None
		name = None

class Metadata(ActiveRecord):
	__TABLE__ = 'metadata'
	class meta:
		id = None
		key = None
		value = None

	def __getattr__(self, key):
		if key == 'file':
			files = Files()
			self.file = files.select("id='" + str(self.id) + "'")
			return self.file
		if self.__dict__.key_exists(key):
			return self.__dict__[key]


if __name__ == "__main__":

	ActiveRecord.database = sqlite.connect("/home/jose/Escritorio/probando.gcatalog")

	catalog = Catalogs()
	print type(catalog)
	print catalog
	catalog.select(1)
	print type(catalog)
#	for d in catalog.disks:
#		print d.name, d.id
#		for f in d.files:
#			print "-- -", f.name
#			for m in f.metadata:
#				print m.key, m.value
#	file = Files()
#	file.select(3)
#	print file.name
#	for i in file.files:
#		print i.name
#		i.name =" ascen "


#	disk = Disks()
#	disk.select(1)

#	for file in disk.files:
#		print file.name, file.disk.name
