# -*- coding: UTF-8 -*-
import gzip
import xml.dom.pulldom
import fstypes
class Cdcat:
	def __init__(self, data):
		self.db = data.db
		self.data = data

	def open(self, filename):
		print "Abriendo ", filename
		data = gzip.open(filename, 'r')
		self.dom = xml.dom.pulldom.parse(data)
		self.__importCdcat(self.dom)
		self.db.commit()
		self.data.load_data()


	def __importCdcat(self, node, idcatalog = 0, iddisk = 0, idparent = 0 ):
		while node:
			node = self.dom.getEvent()
			if not node: return

			if node[0] == 'START_ELEMENT':
				if node[1].nodeType == 1:

					if node[1].tagName == 'catalog':	# creamos el catalogo
						idcatalog = self.db.add_catalog(node[1].attributes['name'].value)
						self.__importCdcat(node, idcatalog)

					elif node[1].tagName == 'media':	# insertamos el disco
						iddisk = self.db.add_disk(node[1].attributes['name'].value, idcatalog, node[1].attributes['name'].value, '/media/cdrom')
						self.__importCdcat(node, idcatalog, iddisk)

					elif node[1].tagName == 'directory':	# Insertamos el directorio
							iddirectory = self.db.add_file(iddisk, idparent, node[1].attributes['name'].value, 0, '', 'x-directory/normal', 'directory')
							self.__importCdcat(node, idcatalog, iddisk, iddirectory)

					elif node[1].tagName == 'file':
							self.db.add_file(iddisk, idparent, node[1].attributes['name'].value, 0, '', '', 'regular')


			if node[0] == 'END_ELEMENT' and (node[1].tagName == 'media' or node[1].tagName == 'catalog' or node[1].tagName == 'directory'):
				return


if __name__ == "__main__":
	info = Info()

	dis = info.get(sys.argv[1])
