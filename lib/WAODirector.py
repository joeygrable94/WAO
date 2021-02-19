'''
CONTROLLER: manages actions between the WAOWindow and Factories
1.	imports app factories
2.	handles input action from WAOWindow
3.	routes action to correct factory method
4.	factory runs method and returns response
5a.	handles factory response data
5b.	handles a factory raised error
6.	returns data or error message to WAOWindow
'''
import sys
try:
	import constants
	from FileFactory import FileFactory, Logger
	from AssetFactory import Asset
	from MetaTagFactory import MetaTags, GeoTags
except:
	from . import constants
	from .FileFactory import FileFactory, Logger
	from .AssetFactory import Asset
	from .MetaTagFactory import MetaTags, GeoTags

def run():
	'''create initial files and folders'''
	WAO = WAODirector()
	LOG = '%s/%s' % (WAO.path_data, 'log.txt')
	try:
		# make console.log file
		FileFactory.makeFile(LOG)
		CONSOLE = Logger( LOG )
	except FileExistsError:
		pass
	# return the director obj.
	return WAO

class WAODirector:
	uploaded = []
	invalid = []

	# -----------------------------------------------------------------------
	# CLASS FUNCTIONS
	def __init__( self ):
		''' constructor '''
		self.index = 0
		self.upload_root = '%s/%s' % (constants.ROOT, 'WAOassets')
		self.path_export = '%s/%s' % (constants.ROOT, '_exports')
		self.path_data = '%s/%s' % (self.upload_root, 'data')
		self.path_ignore = '%s/%s' % (self.upload_root, 'ignored')
		self.path_upload = '%s/%s' % (self.upload_root, 'original')
		self.path_optmze = '%s/%s' % (self.upload_root, 'optimized')
		self.path_geotag = '%s/%s' % (self.upload_root, 'geotagged')
		self.limit = constants.LIMITS
		self.is_download = False
		# build initial file structure
		self.buildFileStructure()

	def __repr__( self ):
		return '<%s uploaded="%d" ignored="%d">' % (
			self.__class__.__name__,
			len(self.uploaded),
			len(self.invalid),
		)

	def setFlag( self, attr, value ):
		if setattr(self, attr, value):
			return True

	def reset( self ):
		# empty all asset objects
		self.uploaded.clear()
		self.invalid.clear()
		# reset index to initial
		self.index = 0
		self.is_download = False
		# rebuild the initial file structure
		self.buildFileStructure()

	def buildFileStructure( self ):
		# make directories
		FileFactory.makeDir(self.upload_root)
		FileFactory.makeDir(self.path_export)
		FileFactory.makeDir(self.path_data)
		FileFactory.makeDir(self.path_ignore)
		FileFactory.makeDir(self.path_upload)
		FileFactory.makeDir(self.path_optmze)
		FileFactory.makeDir(self.path_geotag)
		return True

	def getFileFilteredAssets( self, kind ):
		'''grab a list of file extensions to filter in a QFileDialog'''
		ogkind = kind
		kind = kind[:-1] if kind[-1].lower() == 's' else kind
		filefilter = '%ss (' % (kind.capitalize())
		extlimit = len(constants.MEDIATYPES[kind])
		count = 0
		for ext in constants.MEDIATYPES[kind]:
			filefilter += '*.%s' % (ext)
			if not count == (extlimit-1):
				filefilter += ' '
			count += 1
		filefilter += ');;'
		return str(filefilter)

	def importAsset( self, path_from, filename ):
		# check file valid
		if self.validateAsset( filename ):
			# add the upload file to a list of uploads to manipulate
			aObj = Asset(self.index, filename, path_from, self.path_upload)
			self.uploaded.append( aObj )
			self.index += 1
		else:
			# add the invalid file to a list of uploads to ignore
			aObj = Asset(-1, filename, path_from, self.path_ignore )
			self.invalid.append( aObj )

	def validateAsset( self, filename ):
		''' make sure the file extension is an allowed media type '''
		f_ext = filename.split('.')[-1].lower()
		is_valid = False
		# only images for now
		if f_ext in constants.MEDIATYPES['image']:
			is_valid = True
		# return validation
		return is_valid

	def getAssetByIndex( self, index ):
		''' return the asset object with same the given index '''
		for item in self.uploaded:
			if item.index == int(index):
				return item

	def optimizeImages( self, images, options ):
		# loop all images
		for asset in images:
			if asset.optimizeImage(options):
				asset.setFlag('is_optimized', True)
		return True

	def geotagImages( self, images, options ):
		# loop all images
		for asset in images:
			if GeoTags.tagAssetWithCoords(GeoTags, asset, options['lat'], options['long']):
				asset.setFlag('is_geotagged', True)
		return True
