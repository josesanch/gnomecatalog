# -*- coding: UTF-8 -*-
from pysqlite2 import dbapi2 as sqlite


#import sqlite
import string, os, pprint, tempfile, shutil
import utils, fstypes, thumbnails, config
config = config.Config()
thumbnails = thumbnails.Thumb(config.get('database'))


def dict_factory( cursor, row ):
	d = {}
	for idx, col in enumerate( cursor.description ):
		d[col[0]] = row[idx]
	return d

class DictCursor( sqlite.Cursor ):
	def __init__( self, *args, **kwargs ):
		sqlite.Cursor.__init__( self, *args, **kwargs )
		self.row_factory = dict_factory


class Sqlite:
	database = "gnomeCatalog.gcatalog"
	version = '3.2'

	def __init__( self, dbfile = None, app = None, temp = False ):
		self.database = dbfile
		self.app = app
		self.__deleted_data = False
		self.thumbnails_from_deleted_files = []
		self.thumbnails_from_new_files = []
		self.is_temporal = temp
		if( self.database ):
			if temp:
				self.open_db_temp(dbfile)
			else:
				self.open( self.database)



	def get_version(self):
		rs = self.sql("select value from config where key='version'")
		if len(rs) == 0:
			return '3.0'
		else:
			return rs[0]['value']

	def open_db_temp(self, tmpfile):
		self.database = tmpfile
		self.db = sqlite.connect(self.database) #, isolation_level=None )
		self.cursor = self.db.cursor( factory=DictCursor )
		if not os.path.exists(thumbnails.get_dir()):
			os.mkdir(thumbnails.get_dir())


	def open( self, database):
		self.database = database
		self.database_tempfile = tempfile.mktemp()
		if(os.path.isfile(self.database)): shutil.copyfile(self.database, self.database_tempfile)
		print "Creado :",self.database_tempfile

		self.created = os.path.exists( self.database )
		#self.db = sqlite.connect(database, encoding=('utf-8', 'ignore'))
		self.db = sqlite.connect(self.database_tempfile, isolation_level=None )

		self.cursor = self.db.cursor( factory=DictCursor )

		if not self.created:
			self.__createDB()
		else:
			""" Comprobamos las versiones """
			version = self.get_version()
			""" Actualizamos a la versión actual """
			if version != self.version:
				self.__update_database(version)
				self.save()

	def save(self):
		self.commit()
		self.compress()
		print "Copiando ",self.database_tempfile, " a ", self.database
		shutil.copyfile(self.database_tempfile, self.database)
		""" Ahora tenemos que borrar todos los que tenemos apuntados para borrar """
		self.__delete_thumbnails_from_deleted_files()
		self.thumbnails_from_deleted_files = []
		self.thumbnails_from_new_files = []



	def close(self):
		if self.is_temporal:
			self.commit()
			self.cursor.close()
		else:
#			print "borrando ",self.database_tempfile
			os.remove(self.database_tempfile)
			self.__delete_thumbnails_from_new_files()
			self.thumbnails_from_deleted_files = []
			self.thumbnails_from_new_files = []


	def sql( self, sql ):
		return self.fetchall( self.__sql( sql ) );

	def fetchall( self, result ):
		return self.cursor.fetchall();

	def __sql( self, sql ):
#		print "SQL: ",sql
		command = sql.split( " " )[0].lower()
		if command != "select":
			if command == "delete": self.__deleted_data = True
			self.app.set_guardar_state( True )
		try:
			return self.cursor.execute( sql )
		except sqlite.Error, e:
			print "SQL error occurred:", e.args[0], sql

	def commit( self ):
		self.db.commit()
		#self.__sql("COMMIT")

	def __update_database( self, version ):
		print 'Updating to version ', self.version
		if version == '3.0':
			self.__create_config(self.version)
			self.__sql("ALTER TABLE DISKS ADD COLUMN icon BLOB")
			self.__sql("ALTER TABLE DISKS ADD COLUMN comment VARCHAR")
			self.__sql("ALTER TABLE DISKS ADD COLUMN borrow VARCHAR")
			self.__sql("ALTER TABLE catalogs ADD COLUMN comment VARCHAR")
			self.__sql("ALTER TABLE catalogs ADD COLUMN borrow VARCHAR")
			self.__create_index()
			self.__check_db_integrity()
			self.__extract_thumbnails_from_db()
			self.__sql("DROP TABLE thumbnails")
#			self.__create_trigers()

		if version == '3.1':
			self.__sql("ALTER TABLE DISKS ADD COLUMN borrow VARCHAR")
			self.__sql("ALTER TABLE catalogs ADD COLUMN comment VARCHAR")
			self.__sql("ALTER TABLE catalogs ADD COLUMN borrow VARCHAR")
			self.cursor.execute( "DELETE INDEX metadata_index" )
			self.cursor.execute( "CREATE INDEX IF NOT EXISTS metadata_index ON metadata (id asc, key asc);" )

		self.__sql("update config set value='" + self.version + "' where key='version'")

	def __extract_thumbnails_from_db(self):
		print "Extracting thumbnails from database"
		rows = self.sql("select id, img from thumbnails")
		if not os.path.exists(thumbnails.get_dir()):
			os.mkdir(thumbnails.get_dir())
		for row in rows:
			open('/tmp/gnomecatalog_icon.png', 'wb').write(row['img'])
			thumbnails.save_from_file(row['id'], '/tmp/gnomecatalog_icon.png')


	def __createDB( self ):
		self.__sql( "create table catalogs (id integer PRIMARY KEY, name varchar, idcatalog integer, comment varchar, borrow varchar)" );
		self.__sql( "create table disks (id integer PRIMARY KEY, name varchar, volname varchar, root varchar, idcatalog integer, rating integer, icon BLOB, comment varchar, borrow varchar)" );
		self.__sql( "create table files (id integer PRIMARY KEY, iddisk integer, idparent integer, name varchar, size integer, date timestamp, path varchar, mime varchar, type varchar, comment varchar, rating integer)" );
		self.__sql( "create table metadata (id integer, key varchar, value varchar)" );
#		self.__sql( "create table thumbnails (id integer , img blob);" );
		self.__sql( "create table categories (id integer PRIMARY KEY, name varchar);" );
		self.__sql( "create table rcategoriesfiles (idfile integer, idcategorie integer);" );
		self.__create_config(self.version)
#		self.__create_trigers()
		self.__create_index()

		for c in [_("Movies"), _("Audio"), _("Pictures"), _("Documents")]:
			self.insert_category(c)
		self.created = True

	def __create_index( self ):
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS idcatalog_index ON disks (idcatalog asc);" )
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS iddisk_index ON files (iddisk asc);" )
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS idparent_index ON files (idparent asc);" )
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS metadata_index ON metadata (id asc, key asc);" )
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS rcategories_index ON rcategoriesfiles (idfile asc);" )
#		self.cursor.execute( "CREATE INDEX IF NOT EXISTS thumbnails_index ON thumbnails (id asc);" )

	def __create_config(self, value):
		self.__sql( "create table config (key varchar, value varchar);" )
		self.__sql( "insert into config values ('version', '" + value + "');" )

	""" sqlite3 no soporta triggers recursivos, de momento no son útiles """
	def __create_trigers(self):

		self.cursor.execute( "CREATE TRIGGER trigger_delete_catalog DELETE ON catalogs " +
								"BEGIN" +
									" DELETE FROM catalogs where idcatalog=old.id;" +
									" DELETE FROM disks where idcatalog=old.id;" +
								"END;")

		self.cursor.execute( "CREATE TRIGGER trigger_delete_disks DELETE ON disks " +
								"BEGIN" +
									" DELETE FROM files where iddisk=old.id;" +
								"END;")

		self.cursor.execute( "CREATE TRIGGER trigger_delete_files DELETE ON files " +
								"BEGIN" +
									" DELETE FROM metadata where id=old.id;" +
									" DELETE FROM rcategoriesfiles where idfile=old.id;" +
									" DELETE FROM files where idparent=old.id;" +
								"END;")

		self.cursor.execute( "CREATE TRIGGER trigger_delete_categorie DELETE ON categories " +
								"BEGIN" +
									" DELETE FROM rcategoriesfiles where idcategorie=old.id;" +
								"END;")


	def _check( self, data ):

		txt = str(data)
		try:
			txt = txt.encode("utf-8", "replace")
		except:
			txt = unicode(txt, 'iso-8859-15').encode('utf-8')

		data = string.replace( txt, "'", "")
		return data

	def getFile( self, idfile ):
		metadata = self.sql( "select key, value from metadata where id=" + str( idfile ) )
#		file = self.sql( "select files.*, thumbnails.img as img FROM files left outer join thumbnails on thumbnails.id=files.id where files.id=" + str( idfile ) )
		file = self.sql( "select files.* FROM files where files.id=" + str( idfile ) )
		return [file, metadata]


	def set_categories_to_files(self, ids, categories):
		idstr = ", ".join( [str( i ) for i in ids] )
		self.sql( "DELETE  from rcategoriesfiles where idfile in (" + idstr +  ")" );
		for idfile in ids:
			for cat in categories:
				self.sql( "insert into rcategoriesfiles (idfile, idcategorie) values (" + str( idfile ) + ", " + str( cat ) + ")" )

		self.commit()


	def get_categories( self ):
		result = self.sql( "select id, name from categories order by name" )
		res = []
		for col in result:
			res.append( [col["id"], col["name"]] )
		return res

	def get_categories_from_file(self, id ):
		result = self.sql( "select categories.*, rcategoriesfiles.idfile from categories left outer join rcategoriesfiles on categories.id=rcategoriesfiles.idcategorie and rcategoriesfiles.idfile=" + str( id ) );
		cats = []
		for col in result:
			try:
				if col["idfile"] != None:
					cats.append(col["id"])
			except: pass

		return cats

	def get_metadata_from_file(self, id):
		meta = {}
		result = self.sql( "select key, value from metadata where id=" + str( id ) );
		for item in result:
			meta[item["key"]] = item["value"]
		return meta


	def compress( self ):
		self.cursor.execute( "VACUUM" );



#	def clear_thumbnails(self):
#		self.__sql("DELETE FROM thumbnails")
#		self.commit()


	def insert_category( self, cat ):
		self.__sql( "insert into categories values (Null, '" + cat + "')" )
		return self.cursor.lastrowid;



	""" inserta un disco en la bd """
	def __insert_disk(self, disk):
#		icon = disk.get_icon().get_pixels()
		disk.get_icon().save('/tmp/gnomecatalog_icon_disk.png', 'png')
		data = open('/tmp/gnomecatalog_icon_disk.png', 'rb').read()
		self.cursor.execute( "INSERT into disks (id, name, volname, root, icon, comment, borrow) values (NULL, ?, ?, ?, ?, ?, ?)", (disk.name, self._check(disk.name), self._check(disk.path), buffer(data), disk.comment, disk.borrow));
		return self.cursor.lastrowid;

	""" Inserta los ficheros recursivamente """
	def __insert_files(self, iddisk, idparent, file):
		idparent = self.__insert_file(iddisk, idparent, file)

		if file.is_dir():
			for f in file:
				idfile = self.__insert_files(iddisk, idparent, f)


	def __insert_file(self, iddisk, idparent, file):
		self.__sql( "INSERT into files (id, iddisk, idparent, name, size, path, mime, type) values (NULL, " + str( iddisk ) +", " + str( idparent ) + " ,'" + self._check(file.name) + "', " + str( file.size ) + ", '" +  self._check(file.path) + "', '" + file.mime + "', '" + str( file.type ) + "')" )
		idfile =  self.cursor.lastrowid;

		""" Insetamos los metadatos del fichero """
		if file.meta:
			for key, val in file.meta.items():
				self.__sql( "INSERT into metadata (id, key, value) values (" + str( idfile ) + ", '" + self._check( key ) + "', '" + self._check( val ) + "')" );

		if config.get("thumbnails") == "True":
			thumbnails.save(idfile, file)
			self.thumbnails_from_new_files.append(idfile)


#		thumb = file.get_thumbnail()
#		if thumb:
#			self.cursor.execute("INSERT INTO thumbnails VALUES(?, ?);",(idfile, buffer(thumb)))

		return idfile


	def insert_disk(self, disk):
		iddisk = self.__insert_disk(disk)
		for file in disk:
			self.__insert_files(iddisk, 0, file)

		self.db.commit()
		return fstypes.Disk(disk.name,  disk.path, iddisk, self)

	def insert_catalog(self, catalog):
		self.cursor.execute( "INSERT into catalogs (id, name, comment, borrow) values (NULL, ?, ?, ?)", (catalog.name, catalog.comment, catalog.borrow));
		catalog.id = self.cursor.lastrowid;
		return catalog.id


	""" Funciones usadas en la importacion """
	def add_catalog(self, name):
		self.__sql("INSERT INTO catalogs (id, name) values (NULL, '" + name + "')")
		id =  self.cursor.lastrowid;
		return id

	def add_disk(self, name, idcatalog = '', volname = '', path = ''):
		self.cursor.execute( "INSERT into disks (id, idcatalog, name, volname, root) values (NULL, ?, ?, ?, ?)", (idcatalog, name, self._check(volname), self._check(path)));
		id =  self.cursor.lastrowid;
		return id

	def add_file(self, iddisk, idparent, name, size =  '', path = '', mime = '', mimetype = ''):
		self.cursor.execute( "INSERT into files (id, iddisk, idparent, name, size, path, mime, type) values (NULL, ?, ?, ?, ?, ?, ?, ?)", (iddisk, idparent, name, size, path, mime, mimetype) );
		id =  self.cursor.lastrowid;
		return id



	def read_data(self, idparent = None):
		data = []
		if idparent:
			c_condition = " idcatalog = " + str(idparent)
		else:
			c_condition = "idcatalog=0 or idcatalog is null"

		catalogs = self.sql("select * from catalogs where " + c_condition)
		for c in catalogs:
			data.append(fstypes.Catalog(c["name"],  c["id"], self, c["idcatalog"], c['comment'], c['borrow']))

		disks = self.sql("select * from disks where " + c_condition)
		for c in disks:
			data.append(fstypes.Disk(c["name"],  c["root"], c["id"], self, c["idcatalog"], c["icon"], c['comment'], c['borrow']))

		return data


	def read_files_from_disk(self, disk, idparent = None):
		data = []
		if idparent: c_condition = " idparent = " + str(idparent)
		else: c_condition = "idparent=0 or idparent is null"
		files = self.sql("select * from files where iddisk=" + str(disk.id) + " and " + c_condition + " order by type, id")

		for file in files:
			data.append(fstypes.File(file, disk, self))
		return data

	def search_files(self, search, categorie = None, mime_type = None):
		data = []
		search_cond = ""
		if search: # search in metadata, comment and name
			search_cond = "  and (files.name like '%"  + search + "%' or files.comment like '%" + search + "%' or files.id in (select id from metadata where value like '%" + search + "%'))"

		if categorie:
			sql = "select files.* from files where files.id in (select idfile from rcategoriesfiles where idcategorie='" + str(categorie)  + "') " + search_cond
		elif mime_type:
			sql = "select files.* from files where mime like '" + mime_type + "/%' " + search_cond
		else:
			sql = "select files.* from files where 1=1 " + search_cond

		files = self.sql(sql)
		for file in files:
			data.append(fstypes.File(file, None, self))
		return data

	def update(self, type, id, name, value):
		self.__sql("update " + type +" set " + name + "='" + str( value ) + "' where id=" + str(id))
		self.commit()

	def delete(self, type, id):
		self.__sql("delete from " + type + " where id=" + str(id))

		if type == "categories":
			self.__sql("delete from rcategoriesfiles where idcategorie = " + str(id))

		if type == "files":
			if config.get("thumbnails") == "True":
				self.thumbnails_from_deleted_files.append(id)

			self.__sql("delete from rcategoriesfiles where idfile = " + str(id))
			self.__sql("delete from metadata where id = " + str(id))
#			self.__sql("delete from thumbnails where id= " + str(id))


	def remove_disk(self, id):
		""" Guardamos los thumbnails para luego borrarlos si se guardan los cambios """
		if config.get("thumbnails") == "True":
			files = self.sql("select id from files where iddisk=" + str(id))
			for file in files:
				self.thumbnails_from_deleted_files.append(file['id'])

		self.__sql("delete from disks where id=" + str(id))
		self.__check_db_integrity()


	def __check_db_integrity(self):
#		self.__sql("delete from thumbnails where id in (select id from files where files.iddisk not in (select id from disks))")
		self.__sql("delete from rcategoriesfiles where idfile in (select id from files where files.iddisk not in (select id from disks))")
		self.__sql("delete from metadata where id in (select id from files where files.iddisk not in (select id from disks))")
		self.__sql("delete from files where files.iddisk not in (select id from disks)")
		self.commit()


	def get_duration(self, idfile):
		result = self.cursor.execute("select value from metadata where id='" + str(idfile) + "' and (key='length' or key='duration')").fetchone()
		if result:
			return round(float(result['value']))

	def get_disk(self, id):
		return self.sql("select * from disks where id=" + str(id))

	def get_catalog(self, id):
		return self.sql("select * from catalogs where id=" + str(id))

	def has_deleted_data(self):
		return self.__deleted_data

	def get_categorie_id(self, name):
		result = self.sql("select id from categories where name ='" + name + "'")
		return result[0]["id"]

	def get_totals(self):
		return self.sql("select sum(size) as size, count(*) as count from files")[0]

	def __delete_thumbnails_from_new_files(self):
		for id in self.thumbnails_from_new_files:
			thumbnails.delete(id)

	def __delete_thumbnails_from_deleted_files(self):
		for id in self.thumbnails_from_deleted_files:
			thumbnails.delete(id)
