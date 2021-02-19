'''
VIEW: manages the UI window display:
1. loads the initial interface 
2. routes input actions to WAODirector
3. receives formatted data from WAODirector
4. returns/displays a response to the UI
'''
import sys, os
from screeninfo import get_monitors
from pathlib2 import Path
from tr import tr
from PyQt5 import QtCore
from PyQt5 import QtWidgets as qtw
try:
	import constants
	from FileFactory import FileFactory
	from MetaTagFactory import MetaTags, GeoTags
except:
	from . import constants
	from .FileFactory import FileFactory
	from .MetaTagFactory import MetaTags, GeoTags

def open( WAObj ):
	WAOApp = qtw.QApplication(sys.argv)
	WAOW = WAOWindow( WAObj )
	# open the msg box window
	if WAOApp.exec_():
		# window closed
		WAOApp.resetUI(exit=True)
		sys.exit(WAOApp)

class WAOWindow(qtw.QWidget):
	
	def __init__( self, assets=None ):
		super().__init__()
		self.title = 'WAO'
		self.m = get_monitors()[0]
		self.width = 720
		self.height = 480
		self.left = (self.m.width/2-self.width/2)
		self.top = (self.m.height/2-self.height/2)
		self.wao = assets
		self.initLoader()

	def initLoader( self ):
		self.wao.buildFileStructure()
		# configure window
		self.loader = qtw.QWidget()
		self.loader.setWindowTitle('%s - %s' % (self.title,'loader') )
		self.loader.setGeometry((self.m.width/2-self.width/4), (self.m.height/2-self.height/8), self.width/2, self.height/4)
		self.loader.setLayout(qtw.QGridLayout())
		# inputs
		self.btn_upload_img = qtw.QPushButton('Upload Images')
		self.btn_upload_dir = qtw.QPushButton('Select Folder')
		# connect inputs to actions
		self.btn_upload_img.clicked.connect(self.openImageUploader)
		self.btn_upload_dir.clicked.connect(self.openFolderSelector)
		# add inputs to layout
		self.loader.layout().addWidget(self.btn_upload_img,0,0)
		self.loader.layout().addWidget(self.btn_upload_dir,1,0)
		# set layout and show
		self.loader.show()

	def initUI( self ):
		# close the loader window
		self.loader.close()
		# configure window
		self.setWindowTitle( '%s - %s' % (self.title,'Web Asset Optimizer') )
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.setLayout(qtw.QVBoxLayout())
		# container layout
		self.container = qtw.QWidget()
		self.container_grid = qtw.QGridLayout()
		self.container_grid.setColumnStretch(0,3)
		self.container_grid.setColumnStretch(1,1)
		self.container.setLayout( self.container_grid )
		# upload list
		self.table = qtw.QTableWidget()
		self.table.setSelectionBehavior(qtw.QTableView.SelectRows)
		self.table.setRowCount( len(self.wao.uploaded) )
		self.table.setColumnCount( len(self.wao.uploaded[0].getDict()) )
		self.table.setHorizontalHeaderLabels("ID;file name;optmized;geotagged".split(";"))
		self.table.horizontalHeader().setSectionResizeMode(0, qtw.QHeaderView.ResizeToContents)
		self.table.horizontalHeader().setSectionResizeMode(1, qtw.QHeaderView.Stretch)
		self.table.horizontalHeader().setSectionResizeMode(2, qtw.QHeaderView.ResizeToContents)
		self.table.horizontalHeader().setSectionResizeMode(3, qtw.QHeaderView.ResizeToContents)
		self.table.horizontalHeader().setStretchLastSection(False)
		self.table.verticalHeader().setVisible(False)
		self._setUploadedTableItems( self.wao.uploaded )
		# controls
		self.btn_view_meta = qtw.QPushButton('View Images Metadata')
		self.img_dimensions_label = qtw.QLabel('Image Resize:')
		self.img_width_label = qtw.QLabel('Width:')
		self.img_width_input = qtw.QLineEdit(self)
		self.img_height_label = qtw.QLabel('Height:')
		self.img_height_input = qtw.QLineEdit(self)
		self.img_qlty_label = qtw.QLabel('Image Quality:')
		self.img_qlty_input = qtw.QLineEdit(self)
		self.num_colors_label = qtw.QLabel('Number of Colors:')
		self.num_colors_input = qtw.QLineEdit(self)
		self.btn_optimize = qtw.QPushButton('Optimize Images')
		self.geolocation_label = qtw.QLabel('Geo Tagging:')
		self.geo_address_label = qtw.QLabel('Address Lookup:')
		self.geo_address_input = qtw.QLineEdit(self)
		self.geo_address_lookup_btn = qtw.QPushButton('Get Coordinates')
		self.geo_latitude_label = qtw.QLabel('Latitude:')
		self.geo_latitude_input = qtw.QLineEdit(self)
		self.geo_longitude_label = qtw.QLabel('Longitude:')
		self.geo_longitude_input = qtw.QLineEdit(self)
		self.btn_geotag = qtw.QPushButton('GeoTag Images')
		self.btn_download = qtw.QPushButton('Download Package')
		self.btn_reset = qtw.QPushButton('Reset WAO / Start Fresh!')
		# connect actions
		self.btn_view_meta.clicked.connect(self.openViewMetaData)
		self.btn_optimize.clicked.connect(self.runOptimizeSelected)
		self.geo_address_lookup_btn.clicked.connect(self.lookupGeoCoords)
		self.btn_geotag.clicked.connect(self.runGeotagSelected)
		self.btn_download.clicked.connect(self.runDownloadPackage)
		self.btn_reset.clicked.connect(self.resetUI)
		# add inputs to layout
		self.container.layout().addWidget(self.table,0,0,15,1)
		self.container.layout().addWidget(self.btn_view_meta,0,1,1,1)
		self.container.layout().addWidget(self.img_dimensions_label,1,1,1,1)
		self.container.layout().addWidget(self.img_width_label,2,1,1,1)
		self.container.layout().addWidget(self.img_width_input,2,1,1,1)
		self.container.layout().addWidget(self.img_height_label,3,1,1,1)
		self.container.layout().addWidget(self.img_height_input,3,1,1,1)
		self.container.layout().addWidget(self.img_qlty_label,4,1,1,1)
		self.container.layout().addWidget(self.img_qlty_input,4,1,1,1)
		self.container.layout().addWidget(self.num_colors_label,5,1,1,1)
		self.container.layout().addWidget(self.num_colors_input,5,1,1,1)
		self.container.layout().addWidget(self.btn_optimize,6,1,1,1)
		self.container.layout().addWidget(self.geolocation_label,7,1,1,1)
		self.container.layout().addWidget(self.geo_address_label,8,1,1,1)
		self.container.layout().addWidget(self.geo_address_input,8,1,1,1)
		self.container.layout().addWidget(self.geo_address_lookup_btn,9,1,1,1)
		self.container.layout().addWidget(self.geo_latitude_label,10,1,1,1)
		self.container.layout().addWidget(self.geo_latitude_input,10,1,1,1)
		self.container.layout().addWidget(self.geo_longitude_label,11,1,1,1)
		self.container.layout().addWidget(self.geo_longitude_input,11,1,1,1)
		self.container.layout().addWidget(self.btn_geotag,12,1,1,1)
		self.container.layout().addWidget(self.btn_download,13,1,1,1)
		self.container.layout().addWidget(self.btn_reset,14,1,1,1)
		# set default values
		self.img_width_input.setText( str(self.wao.limit['width']) )
		self.img_height_input.setText( str(self.wao.limit['height']) )
		self.img_qlty_input.setText( str(self.wao.limit['qlty']) )
		self.num_colors_input.setText( str(self.wao.limit['colors']) )
		self.geo_address_input.setText( constants.DEFAULT_ADDRESS )
		self.geo_latitude_input.setText( str(self.wao.limit['latitude']) )
		self.geo_longitude_input.setText( str(self.wao.limit['longitude']) )
		# set layout and show
		self.layout().addWidget(self.container)
		self.updateUI()
		self.show()

	def updateUI( self ):
		# update table items
		self._setUploadedTableItems( self.wao.uploaded )
		# optimize before geotagging
		if self._checkAssetsOptimized( self.wao.uploaded ):
			self.btn_geotag.setEnabled(True)
		else:
			self.btn_geotag.setEnabled(False)
		# optimized and geotagged before download
		if self._checkAssetsReady( self.wao.uploaded ):
			self.btn_download.setEnabled(True)
		else:
			self.btn_download.setEnabled(False)
		# update the geolocation information
		geo_coords = GeoTags.getCoordsFromAddress(GeoTags, str(self.geo_address_input.text()))
		if geo_coords:
			self.geo_latitude_input.setText( str(geo_coords[0]) )
			self.geo_longitude_input.setText( str(geo_coords[1]) )
		else:
			self.geo_latitude_input.setText( str(self.wao.limit['latitude']) )
			self.geo_longitude_input.setText( str(self.wao.limit['longitude']) )
		# if package downloaded
		if self.wao.is_download:
			self.btn_reset.setEnabled(True)
		else:
			self.btn_reset.setEnabled(False)

	def resetUI( self, exit=False ):
		# delete all folder contents
		FileFactory.deleteFolderContents(self.wao.path_export)
		FileFactory.deleteFolderContents(self.wao.upload_root)
		# reset wao director
		self.wao.reset()
		# close the UI
		self.container.close()
		self.close()
		# exit whole app if requested
		if not exit:
			# otherwize re-run loader UI
			self.initLoader()
		return True

	def openFolderSelector( self ):
		dir_dialogue = qtw.QFileDialog()
		options = dir_dialogue.Options()
		options |= dir_dialogue.DontUseNativeDialog
		folder = dir_dialogue.getExistingDirectory( self, "Select a Folder of Images", "/Users/joeygrable/Pictures", dir_dialogue.DontUseNativeDialog | dir_dialogue.ShowDirsOnly | dir_dialogue.DontResolveSymlinks )
		if folder:
			files = self._getUploadList( folder )
			if self._setUploadsList( files ):
				self.initUI()

	def openImageUploader( self ):
		file_dialogue = qtw.QFileDialog()
		options = file_dialogue.Options()
		options |= file_dialogue.DontUseNativeDialog
		ImageFilter = self.wao.getFileFilteredAssets('image')
		files, _ = file_dialogue.getOpenFileNames( self, "Select Images to Upload", "/Users/joeygrable/Pictures", ImageFilter, options=options )
		if files:
			if self._setUploadsList( files ):
				self.initUI()

	def openViewMetaData( self ):
		''' open window to view the selected images' metadata '''
		selected = self._getAssetsByCellIndex( self._getSelectedTableRows(self.table) )
		tag_list = MetaTags.getMetaTagsList(MetaTags, selected)
		self.showMessage('Viewing Image(s) Meta Tags:', tag_list)

	def showMessage( self, title, message, win_title=False ):
		''' open a message window to view a text message '''
		selected = self._getAssetsByCellIndex( self._getSelectedTableRows(self.table) )
		# make msg box
		msgBox = qtw.QMessageBox()
		# set msg box attr
		msgBox.setGeometry((self.m.width/2-self.width/4), (self.m.height/2-self.height/4), self.width/2, self.height/4)
		if win_title:
			msgBox.setWindowTitle( str(win_title) )
		else:
			msgBox.setWindowTitle('WAO! A message for you.')
		msgBox.setStandardButtons(qtw.QMessageBox.Ok)
		msgBox.setText(title)
		# make scroll area in msg box
		msgScroll = qtw.QScrollArea(msgBox)
		msgScroll.setWidgetResizable(True)
		# add the scroll area to a new widget
		content = qtw.QWidget()
		msgScroll.setWidget(content)
		# make a layout in the scroll area widget content
		layout = qtw.QVBoxLayout(content)
		# if single message string
		if type(message) == str:
			# add single message item to the scroll area
			label_text = qtw.QLabel(message, msgBox)
			label_text.setWordWrap(True)
			layout.addWidget( label_text )
		# if list of message strings
		elif type(message) == list:
			# iterate through each message to display
			for item in message:
				# add each item to the scroll area content layout
				label_text = qtw.QLabel(item, msgBox)
				label_text.setWordWrap(True)
				layout.addWidget( label_text )
		# add scroll area to the msg box layout and style it
		msgBox.layout().addWidget(msgScroll, 0, 0, 1, msgBox.layout().columnCount())
		msgBox.setStyleSheet("QScrollArea{min-width: 300px; min-height: %spx} QLabel{min-width: %spx;}"%(str(self.height/2), str(self.width/2)))
		# open the msg box window
		if msgBox.exec_():
			pass # window closed

	def runOptimizeSelected( self ):
		''' get selected images or all, then optimize them '''
		selected = self._getAssetsByCellIndex( self._getSelectedTableRows(self.table) )
		for asset in selected:
			cur_name = asset.getActiveName()
			FileFactory.copyFileFromTo( cur_name, self.wao.path_upload, self.wao.path_optmze )
			new_name = FileFactory.renameFileAppendTo( self.wao.path_optmze, cur_name, 'web' )
			asset.setActiveSrc( self.wao.path_optmze, new_name )
		# get options based on the app inputs
		img_width = int(self.img_width_input.text()) or self.wao.limit['width']
		img_height = int(self.img_height_input.text()) or self.wao.limit['height']
		img_qlty = int(self.img_qlty_input.text()) or self.wao.limit['qlty']
		num_colors = int(self.num_colors_input.text()) or self.wao.limit['colors']
		options = {
			'width': img_width,
			'height': img_height,
			'qlty': img_qlty,
			'colors': num_colors,
		}
		# optimize the images
		if self.wao.optimizeImages(selected, options):
			# update the ui
			self.updateUI()

	def runGeotagSelected( self ):
		''' get selected images or all, then geotag them '''
		selected = self._getAssetsByCellIndex( self._getSelectedTableRows(self.table) )
		for asset in selected:
			cur_name = asset.getActiveName()
			FileFactory.copyFileFromTo( cur_name, self.wao.path_optmze, self.wao.path_geotag )
			new_name = FileFactory.renameFileAppendTo( self.wao.path_geotag, cur_name, 'geo' )
			asset.setActiveSrc( self.wao.path_geotag, new_name )
		# get lat/long from address
		geo_latitude = self.geo_latitude_input.text() or self.wao.limit['latitude']
		geo_longitude = self.geo_longitude_input.text() or self.wao.limit['longitude']
		options = {
			'lat': geo_latitude,
			'long': geo_longitude,
		}
		# geotag the selected images
		if self.wao.geotagImages(selected, options):
			# update the ui
			self.updateUI()

	def lookupGeoCoords( self ):
		# update the ui
		self.updateUI()

	def runDownloadPackage( self ):
		''' check if all assets are optimized and geotagged, then download a ZIP file to '''
		# create a ZipFile object
		zip_file = FileFactory.makeZipFile( path_zip_from=self.wao.upload_root, path_zip_to=self.wao.path_export, filename='WebOptimizedAssets' )
		print(zip_file)
		try:
			# set Mac User download path and move zip there
			download_path = os.path.join(os.path.expanduser("~"), "Downloads")
			if FileFactory.copyFileFromTo( zip_file, self.wao.path_export, download_path ):
				# update ui
				self.wao.setFlag('is_download', True)
				self.showMessage('Download Success', '<p>Your Web Assets are Optimized<br>+ saved to your ~/Downloads folder</p>')
				self.updateUI()
		except:
			# update ui
			self.showMessage('Download Failed', '<p>Oops! We encountered an error when downloading your files.</p>')
			self.updateUI()

	def _checkAssetsReady( self, assets ):
		for item in assets:
			if not item.is_optimized or not item.is_geotagged:
				return False
		return True

	def _checkAssetsOptimized( self, assets ):
		for item in assets:
			if not item.is_optimized:
				return False
		return True

	def _checkAssetsGeoTagged( self, assets ):
		for item in assets:
			if not item.is_geotagged:
				return False
		return True

	def _getUploadList( self, folder ):
		flist = []
		for fa in os.listdir(folder):
			filepath = '%s/%s' % (folder, fa)
			if os.path.isfile(filepath):
				flist.append(filepath)
		return flist

	def _setUploadsList( self, files ):
		for from_path in files:
			filename = from_path.split('/')[-1]
			fileext = filename.split('.')[-1]
			copy_from = '/'.join( from_path.split('/')[0:-1] )
			# import the asset to WAO Director to handle
			self.wao.importAsset( copy_from, filename )
		return True

	def _setUploadedTableItems( self, uploads_dict ):
		for index, asset in enumerate(uploads_dict):
			asdict = asset.getDict()
			# index
			id_cell = qtw.QTableWidgetItem()
			id_cell.setText( str(asdict['id']) )
			# filename
			name_cell = qtw.QTableWidgetItem()
			name_cell.setText(asdict['file'])
			# optimized state
			opt_state = qtw.QTableWidgetItem()
			if asdict['is_opt']:
				opt_state.setText('☑')
			else:
				opt_state.setText('☐')
			opt_state.setTextAlignment(QtCore.Qt.AlignCenter)
			# geotagged state
			geo_state = qtw.QTableWidgetItem()
			if asdict['is_geo']:
				geo_state.setText('☑')
			else:
				geo_state.setText('☐')
			geo_state.setTextAlignment(QtCore.Qt.AlignCenter)
			# set table rows
			self.table.setItem(index,0,id_cell)
			self.table.setItem(index,1,name_cell)
			self.table.setItem(index,2,opt_state)
			self.table.setItem(index,3,geo_state)

	def _getSelectedTableRows( self, table ):
		# first get selected rows
		indexes = table.selectionModel().selectedRows()
		rows = []
		for index in sorted(indexes):
			rows.append( index.row() )
		if not rows:
			rows = range(0,self.wao.index)
		return rows

	def _getAssetsByCellIndex( self, selected ):
		# get asset objects by id
		assets = []
		for row in selected:
			cell_index = self.table.item(row,0).text()
			anAsset = self.wao.getAssetByIndex( cell_index )
			assets.append(anAsset)
		return assets
