from setuptools import setup, find_packages
import py2exe
import glob
import accessible_output2
import libaudioverse

def list_sounds():
	return [('sounds',
		glob.glob('sounds/*.*'))]

setup(
	name = "Shooter",
	author = "Christopher Toth",
	author_email = "q@q-continuum.net",
	packages = find_packages(),
	data_files = accessible_output2.find_datafiles() + libaudioverse.find_datafiles() + list_sounds(),
	options = {
		'py2exe': {
			'compressed': False,
			'excludes': ['win32com.gen_py', 'ingress', 'Tkinter', 'IPython', 'zmq'],
		},
	},
	windows = [{
		'script': 'main.pyw',
		'dest_base': 'Shooter',
	},],
)
