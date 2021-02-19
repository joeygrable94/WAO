import os, shutil
from pathlib2 import Path
from datetime import datetime, date
import functools, operator
import zipfile
try:
	import constants
except:
	from . import constants
'''
FileFactory
Logger (singleton)
'''

class FileFactory:

	__shared_files = {}

	def __repr__( self ):
		return '<%s>' % self.__class__.__name__

	def __init__( self ):
		self.__dict__ = self.__shared_files

	def getSize( self, folder ):
		''' returns the size of the file in KBs to three decimal places'''
		file_bytes = Path(folder).stat().st_size
		file_kbs = file_bytes/1000
		return format(file_kbs, '.3f')

	def getTimestamp( self, folder ):
		''' returns the file last modified timestamp as interger ''' 
		ts = Path(folder).stat().st_mtime
		return int(ts)

	def getFormatedDatetime( self, timestamp ):
		''' returns a datetime string month/day of given the given timestamp '''
		return datetime.utcfromtimestamp( timestamp ).strftime('%m-%d')

	def determineFileType( self, ext ):
		''' returns file type label '''
		filetype = 'unknown'
		for media in constants.MEDIATYPES:
			if ext in constants.MEDIATYPES[media]:
				filetype = media
		return filetype

	def copyFileFromTo( self, filename, path_from, path_to ):
		''' move file from src path to provided path '''
		dest_path = ''
		file_src = Path('%s/%s' % (path_from, filename))
		file_dst = Path('%s/%s' % (path_to, filename))
		try:
			# try moving file to destenation
			dest_path = shutil.copy(file_src, file_dst)
		except IOError as e:
			# create imtermediate directories
			os.makedirs(os.path.dirname(file_dst), exist_ok=True)
			dest_path = shutil.copy(file_src, file_dst)
		return dest_path

	def renameFileAppendTo( self, path_src, old_name, app_str ):
		p = Path('%s/%s'%(path_src,old_name))
		new_name = '%s_%s%s'%(p.stem,app_str,p.suffix)
		p.rename( Path(p.parent, new_name) )
		return new_name

	def deleteFolderContents( self, path_src ):
		try:
			shutil.rmtree(path_src)
		except OSError as e:
			print("Error: %s : %s" % (path_src, e.strerror))
		return True

	def makeDir(self, path):
		''' makes dir if dir does not exist already exist '''
		return Path(path).mkdir(parents=False, exist_ok=True)

	def makeFile(self, filepath):
		''' makes a file if it does not already exist '''
		return Path(filepath).touch(exist_ok=True)

	def makeZipFile( self, path_zip_from, path_zip_to, filename='WebOptimizedAssets'):
		timestamp = self.getTimestamp( path_zip_to )
		timesig = datetime.utcfromtimestamp( timestamp ).strftime('%y-%m-%d')
		zip_filename = '%s-%s.zip' % (timesig, filename)
		zipf = zipfile.ZipFile( '%s/%s'%(path_zip_to, zip_filename), 'w', zipfile.ZIP_DEFLATED)
		for root, dirs, files in os.walk( path_zip_from ):
			for file in files:
				zipf.write( os.path.join(root, file),
					os.path.relpath(os.path.join(root,file), os.path.join(path_zip_from,'..'))
				)
		zipf.close()
		return zip_filename




class Logger:
	__instance = None
	def __new__(cls, val=None):
		if Logger.__instance is None:
			Logger.__instance = object.__new__(cls)
		Logger.__instance.val = val
		return Logger.__instance

	def __repr__( self ):
		return '<%s>' % self.__class__.__name__

	def __init__( self, filepath ):
		self.src = filepath





# instantiate the FileFactory to be imported
if not __name__ == "__main__":
	FileFactory = FileFactory()
