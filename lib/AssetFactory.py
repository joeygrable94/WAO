import os, sys, subprocess
from PIL import ImageFile, Image, ExifTags
ImageFile.LOAD_TRUNCATED_IMAGES = True
from optimize_images import __main__ as optimizer
try:
	import constants
	from FileFactory import FileFactory
except:
	from . import constants
	from .FileFactory import FileFactory
'''
AssetFactory 
'''

class Asset:
	''' handles media information '''
	def __init__( self, aid, filename, path_from, path_to ):
		''' sets up asset values '''
		self.index = aid
		self.name_origin = filename
		self.name = filename
		self.is_optimized = False
		self.is_geotagged = False
		# paths
		self.path_src = path_from
		self.path_dest = path_to
		# set the file origin path (DO NOT EDIT)
		self.file_origin = '%s/%s' % (path_from, filename)
		# move src asset to uploads/original folder
		self.file_source = FileFactory.copyFileFromTo(self.name, self.path_src, self.path_dest)
		# set the active source to the live copy source
		self.active_file = self.file_source
		# WAObj details
		self.ext = self.name.split('.')[-1:][0].lower()
		self.size = FileFactory.getSize( self.file_source )
		self.timestamp = FileFactory.getTimestamp( self.file_source )
		self.modified = FileFactory.getFormatedDatetime( self.timestamp )
		self.type = FileFactory.determineFileType( self.ext )

	def __repr__( self ):
		''' represent asset object by type, size, name, last modified '''
		return '<Asset type=%s size=%skbs modified_on=%s name=%s>' % (self.type, self.size, self.modified, self.name)

	def getDict( self ):
		''' get asset data tuple '''
		asdict = {
			'id': self.index,
			'file': self.name,
			'is_opt':self.is_optimized,
			'is_geo':self.is_geotagged,
		}
		return asdict

	def setFlag( self, attr, value ):
		if setattr(self, attr, value):
			return True

	def setActiveSrc( self, path_new, name_new ):
		self.name = name_new
		self.active_file = '%s/%s' % (path_new, name_new)
		return True

	def getActiveFile( self ):
		''' return active file (full path) '''
		return str(self.active_file)

	def getActiveName( self ):
		''' return active file name '''
		return str(self.name)

	def checkExifTags( self ):
		output = []
		file = self.getActiveFile()
		img = Image.open( file )
		exif = img._getexif()
		output.append( '<h1>%s</h1>'%(img.filename.split('/')[-1]) )
		output.append('<p>')
		if exif:
			for key, val in exif.items():
				try:
					output.append( '<strong>%s</strong>: %s<br>'%(ExifTags.TAGS[key], val) )
				except:
					output.append( '<strong>%s</strong>: %s<br>'%(key,val) )
		else:
			output.append( '<strong>This Asset has NO meta data.</strong>' )
		output.append('<br></p>')
		return ''.join(output)

	def optimizeImage( self, options ):
		# SKIP GIFS
		if self.ext.lower() == 'gif':
			return True
		# calc image case data
		img_case = self.assessImage( options )
		print(img_case)
		max_w = options['width']
		max_h = options['height']
		
		# create optimize-images command
		optimize_cmd = ['optimize-images']
		# optimize_rules = {}
		# optimize_rules['src_path'] = '"%s"' % self.getActiveFile()
		
		# limit image quality
		optimize_cmd.append('-q %s' % options['qlty'])
		# optimize_rules['quality'] = options['qlty']
		
		# JPGs and JPEGs 
		if self.ext.lower() == 'jpg' or self.ext.lower() == 'jpeg':
			# exceeds width
			if img_case[1]:
				optimize_cmd.append('-mw %s' % max_w)
				# optimize_rules['max_w'] = max_w
			# exceeds height
			if img_case[2]:
				optimize_cmd.append('-mh %s' % max_h)
				# optimize_rules['max_h'] = max_h
		# for PNGS
		if self.ext.lower() == 'png':
			# no transparency to preserve
			if not img_case[3]:
				optimize_cmd.append('-rc -mc %s' % options['colors'])
				# optimize_rules['reduce_colors'] = True
				# optimize_rules['max_colors'] = options['colors']
			# exceeds width and height
			if img_case[0]:
				optimize_cmd.append('-cb -fd')
				# optimize_rules['conv_big'] = True
				# optimize_rules['force_del'] = True

		# opt_response = optimizer.main( optimize_rules )
		# print(opt_response)

		# include a link to the src img
		optimize_cmd.append('"%s"' % self.getActiveFile())
		optimizethis = ' '.join(optimize_cmd)
		subprocess.run(optimizethis, shell=True)
		return True

	def assessImage( self, options=None ):
		''' image flags 
		- img-W > web-W = by how much?
		- img-H > web-H = by how much?
		- img-bkg transparent?
		- img-WHR = ratio of width to height?
		'''
		# calc whats needed
		pimg = Image.open( self.active_file )
		w_h = pimg.size
		ratio = float(w_h[0] / w_h[1])
		flag_trans = self._hasTransparency(pimg)
		# check flag - width
		if options['width'] > 0:
			flag_w = True if w_h[0] > options['width'] else False
		else:
			flag_w = True if w_h[0] > constants.LIMITS['width'] else False	
		# check flag - height
		if options['height'] > 0:
			flag_h = True if w_h[1] > options['height'] else False
		else:
			flag_w = True if w_h[0] > constants.LIMITS['width'] else False
		# check flag - size
		flag_size = True if flag_w and flag_h else False
		# check flag - ratio
		flag_ratio = ''
		if ratio == 1:
			flag_ratio = 'square'
		elif ratio > 1:
			flag_ratio = 'landscape'
		elif ratio < 1:
			flag_ratio = 'portrait'
		# return a response
		return (flag_size, flag_w, flag_h, flag_trans)

	def _hasTransparency(self, img):
		''' makes use of the PIL image library to thoroughly
			check if an image is making use of transparency '''
		if img.mode == "P":
			transparent = img.info.get("transparency", -1)
			for _, index in img.getcolors():
				if index == transparent:
					return True
		elif img.mode == "RGBA":
			extrema = img.getextrema()
			if extrema[3][0] < 255:
				return True
		return False
