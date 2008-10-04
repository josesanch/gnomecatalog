# -*- coding: UTF-8 -*-
try:
	import sqlite3
except:
	from pysqlite2 import dbapi2 as sqlite3
import os

class Database:

	default_database = "gnomeCatalog.gcatalog"
	current_version = '3.2'

	def __init__( self, filename = None):
		if filename:
			self.open(filename)

	def open(self, filename):
		print "Abriendo: ", filename
		exists = os.path.exists(filename)
		self.conn = sqlite3.connect(filename)
		self.cursor = self.conn.cursor(  )
		if not exists:
			self.create()

		# Missing code for upgrading the database


	def create(self):
		self.cursor.execute( "create table catalogs (id integer PRIMARY KEY, name varchar, idcatalog integer, comment varchar, borrow varchar)" );
		self.cursor.execute( "create table disks (id integer PRIMARY KEY, name varchar, volname varchar, root varchar, idcatalog integer, rating integer, icon BLOB, comment varchar, borrow varchar)" );
		self.cursor.execute( "create table files (id integer PRIMARY KEY, iddisk integer, idparent integer, name varchar, size integer, date timestamp, path varchar, mime varchar, type varchar, comment varchar, rating integer)" );
		self.cursor.execute( "create table metadata (id integer, key varchar, value varchar)" );
		self.cursor.execute( "create table categories (id integer PRIMARY KEY, name varchar);" );
		self.cursor.execute( "create table rcategoriesfiles (idfile integer, idcategorie integer);" );

		self.__create_config(self.current_version)
		self.__create_index()

		for c in [_("Movies"), _("Audio"), _("Pictures"), _("Documents")]:
			self.cursor.execute( "insert into categories values (Null, '" + c + "')" )


	def __create_index( self ):
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS idcatalog_index ON disks (idcatalog asc);" )
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS iddisk_index ON files (iddisk asc);" )
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS idparent_index ON files (idparent asc);" )
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS metadata_index ON metadata (id asc, key asc);" )
		self.cursor.execute( "CREATE INDEX IF NOT EXISTS rcategories_index ON rcategoriesfiles (idfile asc);" )

	def __create_config(self, value):
		self.cursor.execute( "create table config (key varchar, value varchar);" )
		self.cursor.execute( "insert into config values ('version', '" + value + "');" )



	def upgrade(self):
		pass

	def set_row_factory(self, factory):
		self.conn.row_factory = factory

	def get_cursor(self):
		return self.conn.cursor( )

	def commit(self):
		self.conn.commit()
