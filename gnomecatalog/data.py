# -*- coding: UTF-8 -*-
import gtk, string, pprint, commands, os, pprint, gobject
import gnome, gnome.ui
import gnomevfs
from gnomecatalog.ui import dialogs, treeviews
import utils, storage, reader, config, ui.dialogs, fstypes, csv

icon_theme = gtk.icon_theme_get_default()

class Data:

	def __init__(self, treeDisk, treeFiles, app):
		self.icons = {
					"star_on" : gtk.gdk.pixbuf_new_from_file_at_size(utils.locate_file("star_set.png", "icons"), 16,16),
					"star_off" : gtk.gdk.pixbuf_new_from_file_at_size(utils.locate_file("star_unset.png", "icons"), 16,16)
		}

		self.config = config.Config()
		self.db = storage.Sqlite(None, app)
		self.reader = reader.Reader()
		self.treeFiles = ui.treeviews.Files(treeFiles, self.db)
		self.treeDisk = ui.treeviews.Tree(treeDisk, self.db)
		fstypes.FstypeBase.model_disk  = self.treeDisk.model
		fstypes.FstypeBase.model_files = self.treeFiles.model
		self.app = app
	   	self.__cancel_action = False
		self.__searching = False


	def _mount_callback(self, success, error, detail):
		print "SUCCESS"


	""" Leemos el disco y lo insertamos en la base de datos """
	def import_disk(self):
		path = self.config.get("source")

		database = storage.Sqlite(self.opened_database, self.app, True)

		if self.config.get("thumbnails") == "True":
			if not os.path.exists(database.database + "_thumbs"):
				os.mkdir(database.database + "_thumbs")

		"""Importamos un nuevo disco"""
		if not utils.is_mounted(path):
			self.__path = path
			self.__progress = self.app.progress_bar
			utils.mount(path, self._mount_callback)

		disk = self.reader.read(path, self.app.progress_bar)

		if disk:
			""" ahora insertamos los datos en la base de datos. """
			disk = database.insert_disk(disk)
			if self.config.get("eject") == "True": utils.eject(path)
			self.app.set_guardar_state(True)
#			self.load_data()
#			self.treeDisk.select(disk)
	#		self.show_files_from_selected()
			database.close()
			return disk


	""" Carga los discos de a base de datos en el treeview tree """
	def load_data(self):
		total = self.db.get_totals()
		self.refresh_statusbar(str(total['count'])  + " " + _("files") + " "  + utils.getSize(total['size']))
		self.treeDisk.clear()
		data = self.db.read_data()
		for item in data:
			iter = self.treeDisk.insert(item)

			for i in item:
				if i.is_dir() or i.is_disk() or i.is_catalog():
					iteri = self.treeDisk.insert(i, iter)


	""" Precarga los ficheros en el arbol """
	def preload_data(self, iter):
		model = self.treeDisk.model
		iter = model.iter_children(iter)

		while True:
			if not model.iter_children(iter):
				item = model[iter][3]

				for i in item:
					if i.is_dir() or i.is_disk() or i.is_catalog():
						iteri = self.treeDisk.insert(i, iter)

			iter = model.iter_next(iter)
			if not iter: break

	""" Cuando se pulsa sobre el arbol de discos """
	def show_files_from_selected(self):
		if self.is_searching():
			self.treeDisk.unselect_all()
			return

		self.treeFiles.clear()
		item, iter = self.treeDisk.get_selected()
		for i in item:
			self.treeFiles.insert(i)

		self.refresh_statusbar()

	def cancel_action(self):
		 self.__cancel_action = True

	def selection_size(self):
		return utils.getSize(self.treeFiles.get_size())

	def refresh_statusbar(self, txt = None):
		if txt == None:
			self.app.statusBar.push(0, str(self.treeFiles.count())  + " " + _("files") + " "  + self.selection_size())
		else:
			self.app.statusBar.push(0,txt)

	def search(self, text, categorie):
		self.treeDisk.unselect_all()
		self.__searching = True
		self.app.toolbutton_buscar.set_stock_id(gtk.STOCK_STOP)
		self.refresh_statusbar(_("Searching..."));
		while (gtk.events_pending ()): gtk.main_iteration ();
		self.treeFiles.clear()
		if not categorie[1]:
			files = self.db.search_files(text, categorie = categorie[0] )
		else:
			files = self.db.search_files(text, mime_type = categorie[0] )
		pos= 0

		for i in files:
			if (pos % 100) == 0:
				while (gtk.events_pending ()): gtk.main_iteration ();
			pos = pos + 1
			if self.__cancel_action: break
			self.treeFiles.insert(i, search = True)

		self.__cancel_action = self.__searching = False
		self.app.toolbutton_buscar.set_stock_id(gtk.STOCK_FIND)

		self.refresh_statusbar()
		self.treeDisk.unselect_all()

	def is_searching(self):
		return self.__searching

	def click_on_fileview(self, path = None):
		file = self.treeFiles.get_selected_files()[0]
		if file.is_file():
			self.show_information_dialog()

		if file.is_dir() or file.is_catalog():
			self.treeDisk.select(file)
			self.show_files_from_selected()


	#####################################
	# ACCIONES SOBRE EL LISTADO DE DISCOS Y CATALOGOS
	#####################################

	def new_catalog(self):
		catalog = fstypes.Catalog(_("No name"))
		self.db.insert_catalog(catalog)
		iter = self.treeDisk.insert(catalog)
		self.treeDisk.tree.set_cursor(self.treeDisk.model.get_path(iter), self.treeDisk.column, True)
		self.treeDisk.edit()
		self.app.set_guardar_state(True)


	def __remove_selected_disk(self):
		item, iter = self.treeDisk.get_selected()
		item.delete()

		self.treeDisk.remove(iter)
		self.treeDisk.set_selected(iter)
		self.show_files_from_selected()

	def __remove_selected_files(self):
		files = self.treeFiles.get_selected_files()
		files.reverse()

		for file in files:
			self.treeFiles.remove(file.iter)
			file.delete()


	def remove_selected(self):
		if self.app.treeviewDisk.is_focus():
			self.__remove_selected_disk()

		if self.app.treeviewFiles.is_focus():
			self.__remove_selected_files()

	def show_properties_dialog(self):
		files = self.treeFiles.get_selected_files()
		if len(files) > 0:
			dialogs.PropertiesDialog().run(files, self, callback = self.callback_properties_dialog)

	def show_information_dialog(self):
		files = self.treeFiles.get_selected_files()
		if len(files) > 0: file = files[0]
		else: return
		#f, descripcion = self.getFileInfo(file.id)

		dialogs.InfoDialogs().show(file);

	def callback_properties_dialog(self, files, categories, comment, rating):
		# Ahora las categorias
		cats = []
		insert = False
		for id, check, cat in categories:
			if id == 0:
				id = self.db.insert_category(cat)
				insert = True
			if check: cats.append(id)
		ids = []
		for file in files:
			file.comment = str(comment)
			file.rating = int(rating)
			ids.append(file.id)

		self.app.reload_categories()
		self.db.set_categories_to_files(ids, cats)
		self.treeFiles.reload_file_names()
		#self.show_files_from_selected()



	#####################################
	# DIALOGOS DE FICHEROS
	#####################################


	def open_database(self, file):
		if file != None:

			self.db.open(file)
			self.opened_database = self.db.database_tempfile
			self.config.save("database", file)
			self.treeFiles.clear()
			self.treeDisk.clear()
			gobject.idle_add(self.load_data)
#			self.load_data()

			self.app.mainApp.set_title("Gnome Catalog - " + os.path.basename(file));
			self.app.set_guardar_state(False)

	def save_database(self, clear_thumbnails):
		self.db.save()
		try: self.app.set_guardar_state(False)
		except: pass

	def close_database(self):
		self.db.close()

	def export(self, file, type = 'csv'):
		files = self.db.sql("select disks.name as disk, files.name, files.size from disks, files where disks.id=files.iddisk");
		writer = csv.writer(open(file, "wb"),  dialect='excel', delimiter=',')
		for file in files:
			writer.writerow(file.values())
