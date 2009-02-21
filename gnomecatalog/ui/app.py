# -*- coding: UTF-8 -*-
import sys, gtk, pprint, os, gobject, threading, pango
from gnomecatalog import config, utils, data

from gladeconnect import GladeConnect
import dialogs

try: import sexy
except: has_sexy = False
else: has_sexy = True


class App(GladeConnect):

	def __init__(self, app_info):

 		GladeConnect.__init__(self, "gnomecatalog.glade")

		gobject.threads_init()
		self.app_info = app_info

		self.config = config.Config()
		self.data = data.Data(self.treeviewDisk, self.treeviewFiles, self)
		self.toolbutton_add.set_menu(self.menu_toolbar_add);

		if len(sys.argv) > 1:
			database = sys.argv[1]
		else:
			database  = self.config.get("database")

		self.data.open_database(database)
		self.__id_search = None

	 	self.restore_state()


	def save_state(self):
		"""Guarda el estado"""
		pos = self.mainApp.get_position()
		size = self.mainApp.get_size()
		self.config.save("width", size[0])
		self.config.save("height", size[1])
		self.config.save("left", pos[0])
		self.config.save("top", pos[1])


	def reload_categories(self):
		model = gtk.ListStore(str, str, bool)
		self.combobox_categories.set_model(model)

		model.append([_("Categories") + " / "+  _("File types"), "", False])
		model.append(["@@--types--@@", "@@--types--@@", True])
		for id, name in self.data.db.get_categories():
			model.append([name, id, False])

		self.combobox_categories.set_active(0)
		model.append(["@@--types--@@", "@@--types--@@", True])
		self.combobox_categories.set_row_separator_func(self.__combo_categories)

		for key, name in {"audio" : _("Audio files"), "image" : _("Image files"), "text" : _("Text files"), "video" : _("Video files")}.items():
			model.append([name, key, True])


	def __combo_categories(self, model, iter):
		return model[iter][0] == "@@--types--@@"



	def get_selected_category(self):
		iter=  self.combobox_categories.get_active_iter()
		model =  self.combobox_categories.get_model()
		return [model[iter][1], model[iter][2]]

		#print model[iter][1]
		#self.data.treeFiles.filter(model[iter][1], model[iter][2])
		#if not self.combobox_categories.get_active() == 0:
		#	return self.combobox_categories.get_active_text()
		#return None

	def restore_state(self):
		self.create_search_entry()
		self.create_progress_bar()
		self.mainApp.move(int(self.config.get("left")), int(self.config.get("top")))
		self.mainApp.resize(int(self.config.get("width")), int(self.config.get("height")))
		self.reload_categories()
		self.mainApp.show()


	def create_progress_bar(self):
		self.hbox_import = gtk.HBox()
		self.progress_bar = gtk.ProgressBar()
		self.progress_bar.set_size_request(400, -1)
		self.progress_bar.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
		self.progress_bar.show()

		self.button_import_stop = gtk.Button('Stop', gtk.STOCK_STOP)
		self.button_import_stop.connect("clicked",self.on_import_stop)

		self.button_import_stop.show()

		self.hbox_import.pack_start(self.progress_bar, True, True)
		self.hbox_import.pack_start(self.button_import_stop, False, False)


		self.statusBar.pack_end(self.hbox_import)


	def create_search_entry(self):
		if has_sexy:
			self.search_entry = sexy.IconEntry()
			self.search_entry.set_icon(sexy.ICON_ENTRY_PRIMARY,gtk.image_new_from_stock(gtk.STOCK_FIND,gtk.ICON_SIZE_BUTTON))
			self.search_entry.add_clear_button()
		else:
			self.search_entry = gtk.Entry()

		self.search_entry.connect("changed",self.on_search_changed)

		toolitem = gtk.ToolItem()
		toolitem.add(self.search_entry)
		self.toolbar_top.insert(toolitem, 6)
		self.search_entry.show()
		toolitem.show()
		rc_style = self.search_entry.rc_get_style()
		self.entry_active_style = rc_style.copy()
		self.entry_active_style.base[ gtk.STATE_NORMAL] = rc_style.base[gtk.STATE_SELECTED]
		self.entry_active_style.text[ gtk.STATE_NORMAL] = rc_style.text[gtk.STATE_SELECTED]
		self.entry_active_style.base[ gtk.STATE_ACTIVE] = rc_style.base[gtk.STATE_NORMAL]
		self.entry_active_style.text[ gtk.STATE_ACTIVE] = rc_style.text[gtk.STATE_NORMAL]
		self.entry_active_style.base[ gtk.STATE_SELECTED] = rc_style.base[gtk.STATE_ACTIVE]
		self.entry_active_style.text[ gtk.STATE_SELECTED] = rc_style.text[gtk.STATE_ACTIVE]



	#####################################
	# EVENTOS DE LA VENTANA PRINCIPAL
	#####################################




	def on_toolbutton_preferencias_clicked(self, window):
		dialogs.preferences(self.config)


	def on_combobox_categories_changed(self, widget): pass

		#iter=  self.combobox_categories.get_active_iter()
		#model =  self.combobox_categories.get_model()

		#print model[iter][1]
		#self.data.treeFiles.filter(model[iter][1], model[iter][2])

	#####################################
	# ACCIONES DEL TOOLBAR
	#####################################

	def on_toolbutton_add_clicked(self, window):
		self.hbox_import.show()
#		addDialog = dialogs.addDisk(self.data)
		self.import_thread = threading.Thread(target=self.data.import_disk)
#		self.import_thread.setDaemon(True)
		self.import_thread.start()
		gobject.timeout_add(1000, self.wait_import_cb)

#		t2 = threading.Thread(target=self.wait_import_cb)
#		t2.setDaemon(True)
#		t2.start()

#		gobject.idle_add(self.wait_import_cb, t)

		#dialogs.addDisk(self.data).loadDisk()

	def wait_import_cb(self):
		if not self.import_thread.isAlive():
			self.hbox_import.hide()
			self.data.load_data()
			return False
		return True

	def on_import_stop(self, widget):
		self.data.reader.cancel_import_disk()
		print "stop"


	def on_toolbutton_borrar_clicked(self, window):
		self.data.remove_selected()

	def on_toolbutton_buscar_clicked(self, window):
		if self.data.is_searching():
			self.data.cancel_action()
		else:
			self.data.search(self.search_entry.get_text(), self.get_selected_category())

	def on_search_changed(self, entry, selected_last_selected = False):
		if entry.get_text() != "":
			entry.set_style(self.entry_active_style.copy())
			if self.__id_search != None:  gobject.source_remove(self.__id_search)
			self.__id_search = gobject.timeout_add(800, self.on_search_changed_cb,entry, selected_last_selected)
		else:
			entry.set_style(None)
			self.data.show_files_from_selected()

	def on_search_changed_cb(self, entry, selected_last_selected = False):
#		print "Buscando"
		self.data.search(entry.get_text(), self.get_selected_category())
		return False


	#####################################
	# ACCIONES SOBRE LOS TREEVIEWS
	#####################################
	# Pulsamos sobre el disco o directorio y hay que cargar los discos
	def on_treeviewDisk_row_activated(self,widget, iter, path):
		self.data.show_files_from_selected()

	def on_treeviewDisk_cursor_changed(self, three):
		self.data.show_files_from_selected()

	# Esto es para precargar los directorios al abrirlos
	def on_treeviewDisk_row_expanded(self, widget, iter, path):
		self.data.preload_data(iter)

	# Se pulsa sobre la lista de ficheros.
	def on_treeviewFiles_row_activated(self, widget, iter, column): pass
		#print widget, iter, column
		#self.data.clickOnFiles(iter)


	#####################################
	# ACCIONES DEL MENU
	#####################################
	def on_menu_abrir_activate(self, widget):
		self.data.open_database(dialogs.FileDialogs().open())

	def on_menu_nuevo_activate(self, widget):
		self.data.open_database(dialogs.FileDialogs().new())

	def on_menu_nuevo_catalogo_activate(self, widget):
		self.data.new_catalog()


	def on_menu_compactar_activate(self, window):
		self.data.db.compress()

	def on_treeviewFiles_popup_menu(self, window, event):
		if event.type == gtk.gdk._2BUTTON_PRESS:
			self.data.click_on_fileview()

		if event.button == 3:	# Si se pulsa el boton derecho
			self.menu_files.popup(None,None,None,event.button,  event.time)

		self.data.treeFiles.check_star_clicked(event)


	def on_treeviewDisk_button_press_event(self, widget, event):
		if event.type == gtk.gdk._2BUTTON_PRESS:
			item, iter = self.data.treeDisk.get_selected()
			if item.is_catalog() or item.is_disk():
				dialogs.InfoDiskDialogs(self).show(item)

		if event.button == 3:
			self.menu_disks.popup(None, None, None, event.button, event.time)


	def on_treeviewDisk_key_press_event(self, entry, event):
		if event.keyval == 65471: # f2 key
			self.data.treeDisk.edit()

	def on_treeviewFiles_key_press_event(self, entry, event):
		if event.keyval == 65471: # f2 key
			self.data.treeFiles.edit()

	def on_mainApp_button_press_event(self, entry, event): pass

	def on_renombrar_activate(self, widget):
		self.data.treeFiles.edit()

	def on_menu_disks_rename_activate(self, widget):
		self.data.treeDisk.edit()

	def on_menu_edit_comments_categories_activate(self, window):
		self.data.show_properties_dialog()

	def	on_menu_info_activate(self, window):
		self.data.show_information_dialog()

	def	on_menu_disks_info_activate(self, window):
		dialogs.InfoDiskDialogs().show(self.data.treeDisk.get_selected());



	def on_menu_guardar_activate(self, window):
		self.data.save_database(False)

	def on_guardar_como_activate(self, window):
		self.data.database_filename, clear_thumbnails = dialogs.FileDialogs().save_as()
		self.data.save_database(clear_thumbnails)
		self.data.open_database(self.data.database_filename)

	def on_menu_acercade_activate(self, window):
		dialogs.acercaDe(self.app_info)

	def on_import_menu_activate(self, widget):
		dialogs.Import(self.config, self.data)

	def on_exportar_menu_activate(self, widget):
		dialogs.Export(self.config, self.data)


	def on_menu_quit_activate(self, window, other=None):
		if not self.estado_guardado:
			dialogs.quitDialog(self)
			return True
		else:
			self.quit()

	def quit(self):
		self.data.close_database()
		self.save_state()
		gtk.main_quit()


	def set_guardar_state(self, state):
		self.estado_guardado = not state
		self.toolbutton_guardar.set_sensitive(state)
		self.menu_guardar.set_sensitive(state)
