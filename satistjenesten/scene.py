from pyresample import utils as ps_utils
from copy import deepcopy, copy
from pyresample import kd_tree
from osgeo import gdal, osr

class SatBand(object):
    def __init__(self):
        self.data = None
        self.long_name = None
        self.dtype    = None
        self.unit = None
        self.latitude = None
        self.longitude = None

class GenericScene(object):
    def __init__(self, filepath=None, configpath=None):
        self.file_path = filepath
        self.yaml_dict = configpath
        self.bands = None
        self.longitudes = None
        self.latitudes = None
        self.area_def = None
        self.timestamp = None

    def get_filehandle(self):
        self.filehandle = open(self.file_path, 'r')

    def get_area_def(self, area_name=None):
        if area_name:
            self.area_name = area_name
            self.area_def = ps_utils.load_area('areas.cfg', self.area_name)
        else:
            pass
    def load(self):
        self.get_filehandle()
        self.get_bands()

    def get_coordinates(self):
        if self.area_def is None:
            self.get_area_def()
        self.longitudes, self.latitudes = self.area_def.get_lonlats()

    def resample_to_area(self, target_area_def):
        """
        Resample existing scene to the provided area definition

        """
        attributes_list_to_pass = ['bands', 'timestamp']
        resampled_scene = GenericScene()
        # resampled_scene.bands = deepcopy(self.bands)
        resampled_scene.area_def = target_area_def
        copy_attributes(self, resampled_scene, attributes_list_to_pass)

        try:
            self.area_def = geometry.SwathDefinition(lons=self.longitudes, lats=self.latitudes)
        except:
            self.get_area_def()

        valid_input_index, valid_output_index, index_array, distance_array = \
                kd_tree.get_neighbour_info(self.area_def, resampled_scene.area_def,
                                            self.area_def.pixel_size_x*2.5, neighbours = 1)

        bands_number = len(resampled_scene.bands)
        for i, band in enumerate(resampled_scene.bands.values()):
            print "Resampling band {0:d}/{1:d}".format(i+1, bands_number)
            swath_data = deepcopy(band.data)
            band.data = kd_tree.get_sample_from_neighbour_info('nn', resampled_scene.area_def.shape,
                                                                swath_data,
                                                                valid_input_index,
                                                                valid_output_index,
                                                                index_array)
        return resampled_scene

    def save_geotiff(self, filepath):
        """
        Export Scene in GeoTIFF format
        """
        self.export_path = filepath
        gtiff_driver = gdal.GetDriverByName('GTiff')
        gtiff_format = gdal.GDT_Byte
        bands_number = len(self.bands)
        gtiff_options=["COMPRESS=LZW", "PREDICTOR=2", "TILED=YES"]
        gtiff_options = ["COMPRESS=DEFLATE", "PREDICTOR=2", "ZLEVEL=6", "INTERLEAVE=BAND"]
        gtiff_dataset = gtiff_driver.Create(self.export_path,
                                             int(self.area_def.x_size),
                                             int(self.area_def.y_size),
                                             bands_number,
                                             gtiff_format,
                                             gtiff_options)

        geometry_list = (self.area_def.area_extent[0],
                         self.area_def.pixel_size_x,
                         0,
                         self.area_def.area_extent[3],
                         0,
                         self.area_def.pixel_size_y * -1)

        gtiff_dataset.SetGeoTransform(geometry_list)
        srs = osr.SpatialReference()
        srs.ImportFromProj4(self.area_def.proj4_string)
        gtiff_dataset.SetProjection(srs.ExportToWkt())

        for i, band in enumerate(self.bands.values()):
            print "Writing band #{0:02d}".format(i+1)
            raster_array = band.data
            gtiff_dataset.GetRasterBand(i + 1).WriteArray(raster_array)

        gtiff_dataset = None



def copy_attributes(object_from, object_to, attributes_list):
    for attribute_name in attributes_list:
        if hasattr(object_from, attribute_name):
            the_attribute = getattr(object_from, attribute_name)
            setattr(object_to, attribute_name, deepcopy(the_attribute))












