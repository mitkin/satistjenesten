import unittest
from satistjenesten.mosaic import MosaicScene
from satistjenesten.io import load_mitiff

class TestMosaicScene(unittest.TestCase):
    def setUp(self):
        self.bands_list = [4, 3, 2]
        self.mitiff1 = load_mitiff('test_data/noaa201503111534msv.mitiff', bands=self.bands_list)
        self.mitiff2 = load_mitiff('test_data/noaa201503102141msv.mitiff', bands=self.bands_list)
        self.mosaic = MosaicScene()
        self.mosaic.get_area_def(area_name='istjenesten_main_1k')

    def test_MosaicScene_AddsScenes(self):
        self.mosaic.add_scenes([self.mitiff1])
        self.assertEquals(self.mosaic.start_timestamp, self.mitiff1.timestamp)
        self.assertNotEquals(self.mosaic.area_def, self.mitiff1.area_def)

    def test_MosaicScene_ComposeMosaic(self):
        self.mosaic.add_scenes([self.mitiff1, self.mitiff2])
        self.mosaic.compose_mosaic()
        self.mosaic.save_geotiff('out.tif', bands=self.bands_list)
        self.mosaic.save_rgb_image('rgb.png', self.bands_list)