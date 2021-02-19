from datetime import datetime
import geocoder
from PIL import Image, ExifTags
from GPSPhoto import gpsphoto
try:
	import constants
	from FileFactory import FileFactory
except:
	from . import constants
	from .FileFactory import FileFactory
'''
GeoTagFactory
'''

class MetaTags:

	__shared_tags = {}

	def __repr__( self ):
		return '<%s>' % (
			self.__class__.__name__
		)

	def __init__( self ):
		''' set shared tags '''
		self.__dict__ = self.__shared_tags

	def getMetaTagsList( self, assets ):
		output = []
		for asset in assets:
			tag_str = asset.checkExifTags()
			output.append( tag_str )
		return output

class GeoTags(MetaTags):

	__shared_tags = {}

	def __repr__( self ):
		return '<%s>' % (
			self.__class__.__name__
		)

	def __init__( self ):
		super().__init__( self )
		self.__dict__ = self.__shared_tags

	def getCoordsFromAddress( self, address ):
		if address:
			geo = geocoder.osm(address)
			geo_data = geo.json
			# return the latitude and longitude as tuple
			if geo_data['lat'] and geo_data['lng']:
				return geo_data['lat'], geo_data['lng']
		return False

	def tagAssetWithCoords( self, asset, latitude, longitude, altft=1 ):
		img_coords = ( float(latitude), float(longitude) )
		img_timestamp = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
		filename = asset.getActiveFile()
		# case jpgs
		if asset.ext == 'jpg' or asset.ext == 'jpeg':
			# create a GPSPhoto Object
			photo = gpsphoto.GPSPhoto(filename)
			# create GPSInfo Data Object
			info = gpsphoto.GPSInfo(img_coords, alt=altft, timeStamp=img_timestamp)
			# modify GPS Data
			photo.modGPSData(info, filename)
		# case pngs
		elif asset.ext == 'png':
			print('cannot GEOTag PNGs yet')
		# case gifs
		elif asset.ext == 'gif':
			print('cannot GEOTag PNGs yet')
		return True
