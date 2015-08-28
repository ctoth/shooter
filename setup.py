from setuptools import setup, find_packages
import py2exe
import fnmatch
import glob
import os
import accessible_output2
import libaudioverse

def get_datafiles(directory="share", match="*"):
    """builds list of data files to be with data_files in setuptools
    A typical task in a setup.py file is to set the path and name of a list
    of data files to provide with the package. For instance files in share/data
    directory. One difficulty is to find those files recursively. This can be
    achieved with os.walk or glob. Here is a simple function that perform this
    task.

    .. todo:: exclude pattern
    """
    datafiles = []
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, match):
            matches.append(os.path.join(root, filename))
            this_filename = os.path.join(root, filename)
            datafiles.append((root, [this_filename]))
    return datafiles

def list_sounds():
	return get_datafiles('sounds')

def list_maps():
	return [('', glob.glob('*.yml'))]

def list_docs():
	return [('', glob.glob('*.txt'))]

setup(
	name = "Shooter",
	author = "Christopher Toth",
	author_email = "q@q-continuum.net",
	packages = find_packages(),
	data_files = accessible_output2.find_datafiles() + libaudioverse.find_datafiles() + list_maps() + list_sounds() + list_docs(),
	options = {
		'py2exe': {
			'compressed': False,
			'excludes': ['win32pipe', 'win32com.gen_py', 'ingress', 'Tkinter', 'IPython', 'zmq'],
		},
	},
	windows = [{
		'script': 'main.pyw',
		'dest_base': 'Shooter',
	},],
)
