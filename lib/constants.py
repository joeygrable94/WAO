import os
# ---------------------------------------------------------------------------
# constants
ROOT = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])

MEDIATYPES = {
	#'image': [ 'jpg', 'jpeg', 'jpx', 'png', 'gif', 'webp', 'cr2', 'tif', 'bmp', 'jxr', 'psd', 'ico', 'heic' ],
	'image': [ 'jpg', 'jpeg', 'png', 'gif' ],
	'video': [ 'mp4', 'm4v', 'mkv', 'webm', 'mov', 'avi', 'wmv', 'mpg', 'flv' ],
	'audio': [ 'mid', 'mp3', 'm4a', 'ogg', 'flac', 'wav', 'amr' ],
	'file': [ 'txt', 'pdf', 'rtf', 'epub', 'zip', 'tar', 'rar', 'gz', 'bz2', '7z', 'xz', 'exe', 'swf', 'eot',
				'ps', 'nes', 'crx', 'cab', 'deb', 'ar', 'Z', 'lz', 'hph' ],
	'font': [ 'woff', 'woff2', 'ttf', 'otf' ],
	'code': [ 'xml', 'php', 'py', 'json', 'js', 'html', 'css', 'scss', 'sass', 'less' ],
	'log': [ 'log' ],
	'db': [ 'sqlite', 'sql', 'mmdb' ],
}

LIMITS = {
	'width': 1920,
	'height': 1080,
	'qlty': 100,
	'colors': 255,
	'latitude': 33.78814143905052, # GC Marketing office
	'longitude': -117.84297577732852,
}

DEFAULT_ADDRESS = '1015 E Chapman Ave, Orange, CA 92866'
