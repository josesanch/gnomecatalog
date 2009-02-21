# -*- coding: UTF-8 -*-
import gtk, gnome, gnome.ui
import string, os
from gnomecatalog import utils
from gnomecatalog.ui.gladeconnect import GladeConnect


#####################################
# DIALOGOS DE FICHEROS
#####################################
class FileDialogs:

	def open(self):
		dialog = gtk.FileChooserDialog(_("Open database"),
		                               None,
		                               gtk.FILE_CHOOSER_ACTION_OPEN,
		                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)


		filter = gtk.FileFilter()
		filter.set_name(_("Gnome Catalog Files"))
		filter.add_pattern("*.gcatalog")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name(_("All files"))
		filter.add_pattern("*")
		dialog.add_filter(filter)


		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			file = dialog.get_filename()
		    	dialog.destroy()
			return file
		elif response == gtk.RESPONSE_CANCEL:
			dialog.destroy()
		  	return None
		dialog.destroy()

	def new(self):
		dialog = gtk.FileChooserDialog(_("New database"),
		                               None,
		                               gtk.FILE_CHOOSER_ACTION_SAVE,
		                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)


		filter = gtk.FileFilter()
		filter.set_name(_("Gnome Catalog Files"))
		filter.add_pattern("*.gcatalog")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name(_("All files"))
		filter.add_pattern("*")
		dialog.add_filter(filter)


		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			file = dialog.get_filename()
		    	dialog.destroy()
			if(string.split(file, ".")[0]  != "db"): file = file + ".gcatalog"
			return file
		elif response == gtk.RESPONSE_CANCEL:
			dialog.destroy()
		  	return None
		dialog.destroy()

	def save_as(self):

		dialog = gtk.FileChooserDialog(_("Save as"),
		                               None,
		                               gtk.FILE_CHOOSER_ACTION_SAVE,
		                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)


		filter = gtk.FileFilter()
		filter.set_name(_("Gnome Catalog Files"))
		filter.add_pattern("*.gcatalog")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name(_("All files"))
		filter.add_pattern("*")
		dialog.add_filter(filter)
		check = gtk.CheckButton(_("Don't save thumbnails."))
		dialog.set_extra_widget(check)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			file = dialog.get_filename()
		    	dialog.destroy()
			if(string.split(file, ".")[0]  != "db"): file = file + ".gcatalog"
			return [file, check.get_active()]
		elif response == gtk.RESPONSE_CANCEL:
			dialog.destroy()
		  	return None
		dialog.destroy()




class InfoDialogs(GladeConnect):

	def __init__(self):
		GladeConnect.__init__(self, "dialogs.glade", {"on_info_borrar_activate" : self.on_info_borrar_activate })


	def show(self, file):
		self.glade.get_widget("label_info").set_use_markup(True)


		self.label_info.set_markup(utils.encode(self.get_file_description(file)))

		self.info_filename.set_markup("<b>" + file.name + "</b>   ")
		self.info_fileimage.set_from_pixbuf(file.get_icon(48))
		w, h = self.label_info.get_layout().get_pixel_size()
		self.window_info.show()



	def on_info_borrar_activate(self, widget):
		self.window_info.destroy()

	def get_file_description(self, file):
		txt = "<b>" + _("Type") + ": </b><span foreground=\"darkgray\">"  + file.mime + "</span>\n"
		txt = txt + "<b>" + _("Size") + ": </b><span foreground=\"darkgray\">"  + utils.getSize(file.size) + "</span>\n\n"
		meta = file.get_metadata()

		for key, value in meta.items():
 			txt += "<b>" + key + ": </b><span foreground=\"#565656\">"  + value + "</span>\n"
		return txt


class InfoDiskDialogs(GladeConnect):

	def __init__(self, app):
		self.app = app
		GladeConnect.__init__(self, "dialogs.glade",  { "on_button_disk_cancel_clicked" : self.on_button_cancel, "on_button_disk_accept_clicked" : self.on_button_accept })

	def show(self, item):
		self.disk = item
		self.image_disk.set_from_pixbuf(self.disk.get_icon())

		self.entry_disk_name.set_text(self.disk.name)
		if self.disk.comment:
			self.text_disk_comments.get_buffer().set_text(self.disk.comment)
		if self.disk.borrow:
			self.entry_disk_borrowed.set_text(self.disk.borrow)
		self.window_info_disk.show()


	def on_button_accept(self, widget):
		if self.disk.name != self.entry_disk_name.get_text():
			self.disk.name = self.entry_disk_name.get_text()
			self.app.set_guardar_state(True)

		startiter, enditer = self.text_disk_comments.get_buffer().get_bounds()
		comment = self.text_disk_comments.get_buffer().get_text(startiter, enditer)

		if self.disk.comment != comment:
			self.disk.comment = comment
			self.app.set_guardar_state(True)

		if self.disk.borrow != self.entry_disk_borrowed.get_text():
			self.disk.borrow =  self.entry_disk_borrowed.get_text()
			self.app.set_guardar_state(True)

		self.window_info_disk.destroy()

	def on_button_cancel(self, widget):
		self.window_info_disk.destroy()


class PropertiesDialog(GladeConnect):

	def __init__(self):
		gtk.glade.textdomain("gnomecatalog")
		GladeConnect.__init__(self, "dialogs.glade")

	def run(self, files, data, callback):
		self.callback = callback
		self.files = files
		self.rating = 0

		self.model = gtk.ListStore(int, 'gboolean', str)
		self.tree = self.categories_treeview
		self.tree.set_model(self.model)

		self.data = data
		column = gtk.TreeViewColumn(_("Categories"))
		self.tree.append_column(column)
		cellBool = gtk.CellRendererToggle()
		cellText = gtk.CellRendererText()
		column.pack_start(cellBool, False)
		column.pack_start(cellText, True)
		column.set_attributes(cellText, text=2)
		column.set_attributes(cellBool, active=1)

		cellBool.connect("toggled", self.toggled_cb, (self.model, column))

		if len(files) == 1:
			rating = files[0].rating
			if files[0].comment: comment = files[0].comment
			else: comment = ""
			selected_categories = files[0].get_categories()
		else:
			rating = 0
			comment = ""
			selected_categories = []


		print selected_categories
		for id, cat in data.db.get_categories():
			if id in selected_categories: active = True
			else: active = False
			self.model.append([id, active, cat])



		self.setRating(rating)
		self.glade.get_widget("categories_comment").get_buffer().set_text(comment)
		self.glade.get_widget("window_categories").show()

	def on_eventbox_key_press_event(self, widget, event):
		self.setRating(string.split(widget.name, "_")[1])

	def setRating(self, rating):
		if not rating: rating = 0
		self.rating = rating
		for i in range(1,6):
			print i
			if i > int(rating):
				icon = self.data.icons["star_off"]
			else:
				icon = self.data.icons["star_on"]
			self.glade.get_widget("image_rating_" + str(i)).set_from_pixbuf(icon)

	def on_categories_button_aceptar_activate(self, widget):
		text = self.glade.get_widget("categories_comment")
		startiter, enditer = text.get_buffer().get_bounds()
		comment = text.get_buffer().get_text(startiter, enditer)

		self.callback(self.files, self.model, comment, self.rating)
		self.glade.get_widget("window_categories").destroy()

	def on_categories_button_cancelar_activate(self, widget):
		self.glade.get_widget("window_categories").destroy()

	def toggled_cb(self , cell, path, user_data):
      		model, column = user_data
      		model[path][1] = not model[path][1]
      		return

	def on_button_nuevo_clicked(self, widget):
		dialog = textDialog()
		category = dialog.run(_("New category"), self.newCategory)

	def on_button_quitar_clicked(self, widget):
		(model, iter) = self.tree.get_selection().get_selected()
		if iter:
			self.data.db.delete("categories", model[iter][0])
			model.remove(iter)


	def newCategory(self, text):
		self.model.append([0, False, text])

class textDialog(GladeConnect):

	def __init__(self):
		signals = {
					# Menu
					"on_dialog_button_aceptar_clicked" : self.on_button_accept
					,"on_dialog_button_cancelar_clicked" : self.on_button_cancel
					,"on_dialog_entry_key_press_event" : self.on_dialog_entry_key_press_event
					}
		GladeConnect.__init__(self, "dialogs.glade", signals)

	def run(self, txt, callback):
		self.callback = callback
		self.window_dialog.set_title(txt)
		self.dialog_label.set_text(txt)
		self.window_dialog.show()

	def close(self):
		self.window_dialog.destroy()

	def on_button_accept(self, widget):
		self.callback(self.dialog_entry.get_text())
		self.close()

	def on_button_cancel(self, widget):
		self.close()

	def on_dialog_entry_key_press_event(self, entry, event):
		if event.keyval == 65293:	# Pulsa enter
			self.on_button_accept(entry);

class preferences(GladeConnect):

	def __init__(self, config):

		self.config = config
		GladeConnect.__init__(self, "dialogs.glade")
		self.filechooserbutton_preferences.set_uri(str(self.config.get("source")))
		if self.config.get("eject") == "True": 		self.checkbutton_expulsar.set_active(True)
		if self.config.get("thumbnails") == "True": 	self.checkbutton_thumbnails.set_active(True)

		self.window_preferences.show()

	def on_button_preferences_aceptar_clicked(self, widget):
		self.config.save("source", utils.encode(self.filechooserbutton_preferences.get_uri()))
		self.config.save("eject", self.checkbutton_expulsar.get_active())
		self.config.save("thumbnails", self.checkbutton_thumbnails.get_active())
		self.window_preferences.hide()


	def on_button_preferences_cancelar_clicked(self, widget):
		self.window_preferences.hide()



class addDisk(GladeConnect):

	def __init__(self, data):

		GladeConnect.__init__(self, "dialogs.glade")
		self.addDiskDialog.show()
		self.data = data


	def load_disk(self):
#		self.data = data
		progress = self.progressbar_addDisk
		progress.set_text("");
		progress.show();
		while (gtk.events_pending ()): gtk.main_iteration ();

		iddisk = self.data.import_disk(self.data.config.get("source"), progress);

		self.on_add_cancel(True)
#		self.data.load_data()
#		self.data.treeDisk.select_item(iddisk)	 # hay que hacer que edite
#		self.data.show_files_from_selected()
#		self.data.eject()


	def on_add_cancel(self, window):
		self.data.reader.cancel_import_disk()
		self.addDiskDialog.hide()


class quitDialog(GladeConnect):

	def __init__(self, app):
		self.app = app
		GladeConnect.__init__(self, "dialogs.glade")
		self.dialog_quit.show()

	def on_button_quit_guardar_clicked(self, window):
		self.app.data.save_database(False)
		self.app.quit()


	def on_button_quit_cancelar_clicked(self, window):
		self.dialog_quit.hide()

	def on_button_quit_cerrar_sin_guardar_clicked(self, window):
		self.app.quit()


class acercaDe(gtk.AboutDialog):

	def __init__(self, app_info):
		gtk.AboutDialog.__init__(self)
		self.set_name(app_info['name'])
		self.set_version(app_info['version'])
		self.set_website("http://gnomecatalog.sf.net")
		self.set_website_label("http://gnomecatalog.sf.net")
		self.set_authors(app_info['authors']);
		self.set_translator_credits(app_info["translators"])
		self.set_logo(gtk.gdk.pixbuf_new_from_file(utils.locate_file('gcatalog.png', "icons"), ));
		self.set_copyright("Copyright (c) 2004-2007 José Sánchez Moreno.");
		self.set_comments("Gnome Catalog program.")
		self.run()
		self.destroy()

class Export(gtk.FileChooserDialog):

	def __init__(self, config, data):
		gtk.FileChooserDialog.__init__(self, _("Export database"),
		                               None,
		                               gtk.FILE_CHOOSER_ACTION_SAVE,
		                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))


		combo = gtk.combo_box_new_text()
		combo.append_text("csv")
#		combo.append_text("HTML")
#		combo.append_text("XML Tellico")
		combo.set_active(0)

		self.set_extra_widget(combo)

#		filter = gtk.FileFilter()
#		filter.set_name(_("Gnome Catalog Files"))
#		filter.add_pattern("*.gcatalog")
#		self.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name(_("All files"))
		filter.add_pattern("*")
		self.add_filter(filter)

		response = self.run()
		if response == gtk.RESPONSE_OK:
			file = self.get_filename()
			if(len(string.split(os.path.basename(file), ".")) == 1): file = file + ".csv"
			self.destroy()
			data.export(file, 'csv')

		elif response == gtk.RESPONSE_CANCEL:
			self.destroy()




class Import(gtk.FileChooserDialog):

	def __init__(self, config, data):
		gtk.FileChooserDialog.__init__(self, _("Import database"),
		                               None,
		                               gtk.FILE_CHOOSER_ACTION_OPEN,
		                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))

		filter = gtk.FileFilter()
		filter.set_name(_("Cdcat files"))
		filter.add_pattern("*.hcf")
		self.add_filter(filter)

		response = self.run()
		if response == gtk.RESPONSE_OK:
			file = self.get_filename()
			self.destroy()
			from gnomecatalog import importdata
			imp = importdata.Cdcat(data)
			imp.open(file)



		elif response == gtk.RESPONSE_CANCEL:
			self.destroy()
