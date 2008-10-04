import os, commands, time
import gnomevfs, gtk

def locate_file(path, type = "icons"):
	prefixes = ['', 'usr/', 'usr/local/']
	if type == "glade":
		subs = ["share/gnomecatalog/glade", "share/glade"];

	elif type == "icons" or  type == "pixmap":
		subs = ["share/gnomecatalog/pixmaps", "share/pixmaps"];


	# Try them locally
	for prefix in prefixes:
		for sub in subs:
			if os.path.exists(prefix + os.path.join(".." ,sub, path)):
				return prefix + os.path.join(".." ,sub, path);
	# Try them from root
	for prefix in prefixes:
		for sub in subs:
			if os.path.exists('/' + prefix + os.path.join(sub, path)):
				return '/' + prefix + os.path.join(sub, path)


	return None


def getSize(size):
	if not size or size == None: return ""
	if size > 1024 * 1024 * 1024:
		return str(round(float(size) / (1024 * 1024 * 1024),2)) + " Gb"
	elif size > 1024 * 1024:
		return str(size / (1024 * 1024)) + " Mb"
	elif size > 1024:
		return str(size / 1024) + " Kb"
	else:
		return str(size) +	"b"

def get_length(secs):
	txt = ""
	t = time.localtime(secs)
	hour = t[3] - 1
	minute = t[4]
	sec = t[5]
	if hour > 0: txt = txt + str(hour) + "h "
	txt = txt + str(minute) + "m"
	if hour == 0: txt = txt + " " +  str(sec) + "s"
	return txt

def encode(txt):
#	txt = unicode(txt, "utf-8")
	txt = str(txt).replace("&", "&amp;")

	try:
		txt  =txt.encode("utf-8", "replace")
	except:
		txt = unicode(txt, 'iso-8859-15').encode('utf-8')


	return txt


def get_label(path):
	drive = gnomevfs.VolumeMonitor().get_volume_for_path(path)
	if drive:
		print "label:",drive.get_display_name()
		return drive.get_display_name()

def callback_eject(data, data1, data2): pass

def eject(path):
	print "EJECT: " + path
	drives = gnomevfs.VolumeMonitor().get_connected_drives()
	for drive in drives:
		if drive.get_activation_uri() == path:
			return drive.eject(callback_eject)	# Callback dont work
		volumes = drive.get_mounted_volumes()
		for volume in volumes:
			if volume.get_activation_uri() == path:
				drive.eject(callback_eject)

def is_mounted(path):
	drives = gnomevfs.VolumeMonitor().get_connected_drives()
	for drive in drives:
		if drive.get_activation_uri() == path and drive.is_mounted(): return True
	return False

def get_drive_icon(path):
	icon_theme = gtk.icon_theme_get_default()
	volume = gnomevfs.VolumeMonitor().get_volume_for_path(path)
	icon =  icon_theme.load_icon(volume.get_icon(), 24, 0)
	return icon

def callback_mount(data, data1, data2):
	print "Dont work"


def mount(path, callback):
	print "Montando " + path
	drives = gnomevfs.VolumeMonitor().get_connected_drives()
	for drive in drives:
		if drive.get_activation_uri() == path:
			drive.mount(callback)
			time.sleep(2)

if __name__ == "__main__":
#	path = "/media/cdrom0"
	path = "/home/jose/Escritorio/Descargas/Sober"
	icon = get_drive_icon(path)
	icon.save('/home/jose/Escritorio/tmp_gnomecatalog_icon.png', 'png')

	drives = gnomevfs.VolumeMonitor().get_connected_drives()
	volume = gnomevfs.VolumeMonitor().get_volume_for_path(path)
	print volume.is_mounted()
	print dir(volume)
	for drive in drives:
#		print dir(drive)
		print drive.get_activation_uri()
		if drive.get_activation_uri() == path:
			print path
#			drive.mount(mounted)
