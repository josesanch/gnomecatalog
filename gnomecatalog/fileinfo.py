# -*- coding: UTF-8 -*-
# Gstreamer 0.10
#import gobject
#import pygst
#pygst.require('0.10')
#from gst.extend import discoverer
#import gst
#import EXIF
#import mmpython
import kaa.metadata

import gnomevfs, os, string, sys, urllib

class Info:
	def __init__(self): pass

	def get(self, file):
		meta = {}
		img = None
#		print  "FILEINFO: " + file
		file_path, file_name, file_type, file_size, file_mime = self.__stat(file)
		try:
			path = urllib.url2pathname(str(file))[7:]
#			path = file
			meta = self.__kaa(path)
			#if file_mime == "image/jpeg":
			#	meta = self.__image(file)
			#else:
#				meta = self.__gstreamer(file)

		except: pass
#		print meta
		return file_path, file_name, file_size, file_type, file_mime, meta


	def __kaa(self, filename):
		meta = {}
		info = kaa.metadata.parse(filename)
		for i in info.keys():
			value = info.get(i)

			if isinstance(value, list):
				for lista in value:
					for item in lista.keys():
						val = lista.get(item)

						if val != None:
							meta[i + '_' + item] = val

			elif value != None and i != 'thumbnail':
				meta[i] = value

		return meta


	def __mmpython(self, file):
		meta = {}
		info = mmpython.parse(file)
#		print info

		if info:
			tables = ["video", "audio", "image"]
			not_save = ["dict", "i18ndir", "url", "name"]
			for table in tables:
				if info.has_key(table):
					mediums = info[table]
					for medium in mediums:
						for key in medium.keys:
							if medium[key] and key not in not_save:
								meta[table + "_" + key] = medium[key]

			for table in info._tables:
				mm = info._tables[table]
				for key, value in mm.__dict__.items():
					if value and key not in not_save:
						meta[key] = value

			for key in info.keys:
				if info[key] and key not in not_save:
					meta[key] = info[key]

		return meta

	def __image(self, file):
		meta = {}
		try:
			tags = EXIF.process_file(open(file, 'rb'))
		except:
			tags = {}

		for item in  ("EXIF ApertureValue",  "EXIF BrightnessValue",
					   "EXIF ColorSpace",
					   "EXIF ComponentsConfiguration",
					   "EXIF DateTimeDigitized",
					   "EXIF ExifImageLength",
					   "EXIF ExifImageWidth",
					   "EXIF ExifVersion",
					   "EXIF ExposureBiasValue",
					   "EXIF ExposureProgram",
					   "EXIF ExposureTime",
					   "EXIF FNumber",
					   "EXIF Flash",
					   "EXIF FlashEnergy",
					   "EXIF FlashPixVersion",
					   "EXIF FocalLength",
					   "EXIF ISOSpeedRatings",
					   "EXIF InteroperabilityOffset",
					   "EXIF LightSource",
					   "EXIF MeteringMode",
					   "EXIF ShutterSpeedValue",
					   "EXIF SubjectDistance",
					   "Image Model", "Image Make", "EXIF MaxApertureValue","EXIF MeteringMode", "EXIF SensingMethod", "JPEGThumbnail"):
			if tags.has_key(item):
				if tags[item] != None : meta[item] = tags[item]
		return meta

	def __stat(self, file):
		self.cwd = gnomevfs.URI(os.getcwd())
		if str(self.cwd)[-1] != '/': self.cwd = self.cwd.append_string('/')
		file_uri = self.cwd.resolve_relative(file)
		try:
			file_info = gnomevfs.get_file_info(file_uri, gnomevfs.FILE_INFO_GET_MIME_TYPE)
		except:
			class file_info:
				name = file
				file_type = ""
				file_size = 0
				mime = ""
#			print 'Name:	  ', file_info.name

		file_type = '(none)'
		try: file_type = ('unknown', 'regular', 'directory',
						  'fifo', 'socket', 'chardev', 'blockdev',
						  'symlink')[file_info.type]
		except: pass
#			print 'Type:	  ', file_type

		file_size = '(unknown)'
		try:
			file_size = file_info.size
		except:
			file_size = 0
#			print 'Size:	  ', file_size

		mime_type = '(none)'
		try: mime_type = file_info.mime_type
		except: pass
		#print 'Mime type: ', mime_type
		return file_uri, file_info.name, file_type, file_size, mime_type


	def _discovered_cb(self, discoverer, ismedia):
		self.discoverer = discoverer
		self.discovered = True
		gobject.idle_add(self.loop.quit)
		return True

	def discover(self):
		discover = discoverer.Discoverer(self.filename)
		discover.connect('discovered', self._discovered_cb)
		discover.discover()

	def __gstreamer(self, filename):
#		print "INFORMACIÓN GSTREAMER";
		Discoverer(filename).print_info()


		return
		self.filename = filename
		self.loop = gobject.MainLoop()
		gobject.idle_add(self.discover)
		self.loop.run()
		self.discovered = False
		self.discover()

		discoverer = self.discoverer
		info = {}
		info = discoverer.tags
		#print dir(info["date"])
		#info["date"] = str(info["date"].)
		info["duration"] = max(discoverer.audiolength, discoverer.videolength)

		if discoverer.is_audio:
			info["audio"] = "%d channel(s) %dHz" % (discoverer.audiochannels,
														discoverer.audiorate)
		if discoverer.is_video:
			info["video"] = "%d x %d at %d/%d fps" % (discoverer.videowidth,
														  discoverer.videoheight,
														  discoverer.videorate.num,
														  discoverer.videorate.denom)
		self.loop.quit()
		return info

	def gs2(self, filename):
#		print filename
		discover = discoverer.Discoverer(filename)
		discover.discover()
		while 1:
			if not discover.audiolength:
				continue

	# Extract tags with gstreamer is too slow, not used at the moment
	def gs(self, filename):

		pipeline = gst.parse_launch("filesrc name=source ! decodebin name=demux ! fakesink")
		source = pipeline.get_by_name("source")
		source.set_property("location", filename)
		demux = pipeline.get_by_name("demux")
		self.bus = pipeline.get_bus()
		pipeline.set_state(gst.STATE_PLAYING)

		while 1:
			msg = self.bus.poll(gst.MESSAGE_ANY , gst.SECOND)
			print msg
			if msg:
				if msg.type == gst.MESSAGE_EOS: break
				if msg.type == gst.MESSAGE_TAG:
					print msg
			else:
				break;

		pipeline.set_state(gst.STATE_NULL)

if __name__ == "__main__":
	info = Info()

	dis = info.get(sys.argv[1])
