# -*- coding: UTF-8 -*-
import gtk, string
import gobject

from gnomecatalog import utils

class Tree:
	def __init__(self, tree, db):
		self.tree = tree
		self.db = db
		self.model = gtk.TreeStore(int, str, gtk.gdk.Pixbuf, gobject.TYPE_PYOBJECT)
		self.tree.set_model(self.model)
		self.tree.set_reorderable(True)
		self.tree.set_rules_hint(True)	# Alternal el color de las filas
		self.column = gtk.TreeViewColumn(_("Disks"))
		self.tree.append_column(self.column)
		self.cellicon = gtk.CellRendererPixbuf()
		self.cellicon.set_property('xpad', 2)
		self.cell = gtk.CellRendererText()
		self.cell.set_property('editable', False)

		self.cell.connect('edited', self.edited_cb, self.model)
		self.cell.connect('editing-started', self.editing_started, self.model)
		self.column.pack_start(self.cellicon, False)
		self.column.pack_start(self.cell, True)
		self.column.set_attributes(self.cellicon, pixbuf=2)
		self.column.set_attributes(self.cell, markup=1)
		self.tree.set_search_column(True)
		self.column.set_sort_column_id(1)

		self.tree.connect("drag_data_received", self.drag_data_received_data)

	def edit(self):
		(model, pathlist) = self.tree.get_selection().get_selected_rows()
		if len(pathlist) == 0: return
		path = pathlist[0]
		self.tree.get_selection().select_path(path)
		self.cell.set_property('editable', True)
		self.tree.set_cursor(path, self.column, start_editing=True)

	def drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
		source_path = selection.data[4:]	# path del source
		source_item = self.get_item(self.model.get_iter(source_path))
		drop_info = treeview.get_dest_row_at_pos(x, y)

		if drop_info:
			path, position = drop_info
			dest_item = self.get_item(self.model.get_iter(path))
			if(position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
				if dest_item.is_catalog():
					source_item.idcatalog = dest_item.id
					return True
		else:
			if source_item.is_dir(): return False
		source_item.idcatalog = 0

	def get_item(self, iter):
		return self.model[iter][3]

	def edited_cb(self, cellrenderer, row , value, model):
		item = self.get_item(row)
		model[row][1] = item.name = value
		self.cell.set_property('editable', False)

	def unselect_all(self):
		self.tree.get_selection().unselect_all()

	def editing_started(self, cell, editable, path, data):
		item = self.model[path][3]
		if item.is_dir():
			editable.destroy()
			return False

	def select(self, item):
		iter = self.model.foreach(self.__select_handler, item)
		self.set_selected(self.__searchIter)

	def __select_handler(self, model, path, iter, item =  None):
		file = self.get_item(iter)
		found = False
		if item.is_catalog():
			if file.id  == item.id and file.is_catalog(): found = True
		elif item.is_disk():
			if file.id  == item.id and file.is_disk(): found = True
		elif item.is_dir():
			if file.id  == item.id and file.is_dir(): found = True

		if found:
			self.__searchIter = iter
			return True


	def clear(self):
		self.model.clear()

	def insert(self, item, iter = None):
		iter = self.model.append(iter, [item.id, item.get_text(), item.get_icon(), item])
		item.iter = iter
		return iter

	def set_value(self, iter, column, value):
		self.model.set_value(iter, column, value)

	def get_selected(self):
		(model, iter) = self.tree.get_selection().get_selected()
		return model[iter][3], iter

	def set_selected(self, iter):
		try: self.tree.expand_to_path(self.model.get_path(iter))
		except: pass
		self.tree.get_selection().select_iter(iter)

	def remove(self, iter):
		self.model.remove(iter)



class Files:
	color = '#606060'
	def __init__(self, tree, db):
		self.tree = tree
		self.db = db
		self.icons = {
                    "star_on" : gtk.gdk.pixbuf_new_from_file_at_size(utils.locate_file("star_set.png", "icons"), 16,16),
                    "star_off" : gtk.gdk.pixbuf_new_from_file_at_size(utils.locate_file("star_unset.png", "icons"), 16,16)
        }
		self.edit_enabled = True

		# texto, tamaño, icono, item, size, rating
		# 0       1      2       3     4      5
		self.model = gtk.ListStore(str, str,  gtk.gdk.Pixbuf, gobject.TYPE_PYOBJECT, int, int)
		self.tree.set_model(self.model)

		self.tree.set_reorderable(False)
		self.tree.set_headers_clickable(True)
		self.tree.set_rules_hint(True)

		self.tree.set_search_column(0)


		column = gtk.TreeViewColumn(_("Files"))
		column.set_resizable(True)
		column.set_clickable(True)
		column.set_reorderable(True)
		column.set_expand(True)
		column.set_sort_column_id(0)
		self.file_column = column


		celltext = gtk.CellRendererText()


		column2 = gtk.TreeViewColumn(_("Size"), celltext, markup=1)
		column2.set_resizable(True)
		column2.set_clickable(True)
		column2.set_sort_column_id(4)

		column3 = gtk.TreeViewColumn(_("Rating"))
		column3.set_resizable(True)
		column3.set_clickable(True)
		column3.set_sort_column_id(5)


		for i in range(1, 6):
			renderer_pixbuf = gtk.CellRendererPixbuf()
			if i == 1:
				renderer_pixbuf.set_property('xalign', 1.0)
				renderer_pixbuf.set_property('width', 25)
			column3.pack_start(renderer_pixbuf, False)
			column3.set_cell_data_func(renderer_pixbuf, self.cell_paint_rating, i)

		column3.set_max_width(120)
		column3.set_alignment(0)
		self.column_star = column3
		self.tree.append_column(column)
		self.tree.append_column(column2)
		self.tree.append_column(column3)

		cellicon = gtk.CellRendererPixbuf()
		cellicon.set_property('xpad', 2)

		renderer = gtk.CellRendererText()
#		renderer.set_property('editable', True)
		self.renderer = renderer


		renderer.connect('edited', self.edited_cb, self.model)
		renderer.connect('editing-started', self.edited_started, self.model)

		column.pack_start(cellicon, False)
		column.pack_start(renderer, True)

		column.set_attributes(cellicon, pixbuf=2)
		column.set_attributes(renderer, markup=0)

		self.tree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

		#self.modelfilter = self.model.filter_new()
		#self.modelfilter.set_visible_func(self.__filter_func)
		#self.tree.set_model(self.modelfilter)

	def edit(self):
		(model, pathlist) = self.tree.get_selection().get_selected_rows()
		if len(pathlist) == 0: return
		path = pathlist[0]
		self.tree.get_selection().select_path(path)
		self.renderer.set_property('editable', True)
		self.tree.set_cursor(path, self.file_column, start_editing=True)

	""" Paint rating """
	def cell_paint_rating(self, column, cell, model, iter, data):
		item = self.get_item(iter)
		if item.is_file():
			if data <= item.rating:
				cell.set_property('pixbuf', self.icons["star_on"])
			else:
				cell.set_property('pixbuf', self.icons["star_off"])


	def edited_started(self, cell, editable, path, data):
		item = self.get_item(path)
		if not self.edit_enabled or item.is_disk() or item.is_catalog():
			editable.destroy()
			return False
		self.renderer.set_property('editable', False)
		editable.set_text(item.name)


	def get_item(self, iter):
		return self.model[iter][3]

	def edited_cb(self, cellrenderer, row , value, model):
		item = self.get_item(row)
		txt = ""
		if item.comment: txt = txt + "\n<span foreground=\""+ self.color +"\"><small>" + item.comment + "</small></span>"
		self.model[row][0] = utils.encode(value + txt)
		item.name = value

	def count(self):
		return len(self.model)

	def clear(self):
		self.model.clear()

	def reload_file_names(self):
		self.model.foreach(self.__foreach_reload_file_names)

	def __foreach_reload_file_names(self, model, path, iter, value = None):
		item = self.get_item(iter)
		self.model[iter][0] = self.__get_item_text(item)

	def insert(self, item, iter = None, search = False):
		if item.size == None: size = 0
		else: size = item.size
		size_txt = "<span foreground=\""+ self.color +"\"><small>" + utils.getSize(item.size) + "</small></span>";

		if item.rating == None: rating = 0
		else: rating = item.rating

		iter = self.model.append([self.__get_item_text(item, search), size_txt, item.get_icon(), item, size, rating])
		item.iter = iter
		return iter

	def __get_item_text(self, item, search = False):
		text = item.name
		if search:
			text = text + "\n<span foreground=\""+ self.color +"\"><small><b>" + item.get_location() + "</b></small></span>"

		if item.comment: text = text + "\n<span foreground=\""+ self.color +"\"><small>" + item.comment + "</small></span>"

		if item.is_file():
			duration = item.get_duration()
			if duration:
				text = text + "<span foreground=\""+ self.color +"\"><small>     (" +  utils.get_length(float(duration)) 	 + ")</small></span>"
		return text

	def get_size(self):
		self.__size = 0
		self.model.foreach(self.foreach_handler_dirs)
		return self.__size

	def foreach_handler_dirs(self, model, path, iter, value = None):
	    	self.__size =self.__size + model[iter][4]

	def get_selected_files(self):
		(model, pathlist) = self.tree.get_selection().get_selected_rows()
		files = []
		for path in pathlist:
			files += [model[path][3]]
		return files

	def remove(self, iter):
		self.model.remove(iter)

	def filter(self, data, filter_mime):
		self.__filter_data = data
		self.__filter_mime_type = filter_mime
		self.modelfilter.refilter()


	def __filter_func(self, model, iter):
		item = model[iter][3]

		if item and self.__filter_data != "":
			if self.__filter_mime_type:
				item.mime.split("/")
				return type == self.__filter_data
			else:
				return item.get_categories().count( int(self.__filter_data)) > 0

		return True

	def check_star_clicked(self, event):
		try:
			path, column, x, y = self.tree.get_path_at_pos(int(event.x), int(event.y))
			if self.column_star == column:
				if x > 10:
					star = ((x - 10) / 16)  + 1
				else: # If you click out of the stars
					star = 0

				if star > 5: star = 0
				item = self.get_item(path)
				item.rating = star
		except: pass
