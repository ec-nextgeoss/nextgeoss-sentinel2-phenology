import requests
import json
import pandas as pd
import datetime
import geopandas as gpd
import rasterio
from rasterio import features
import subprocess

class Rasterizer:

    def writeToShapefile(self, out_file, shapes):
        features = gpd.GeoDataFrame.from_features(shapes)
        features.crs = {'init': 'epsg:4326'}
        features = features.to_crs({'init': 'epsg:3857'})
        features.to_file(out_file)

    def rasterize(self, in_shape, out_tiff):
        bounds = gpd.read_file(in_shape).total_bounds
        buffer = 100
        cmd = ' '.join(['gdal_rasterize', '-a_nodata', '0', '-a', 'value', '-ot', 'UInt16', '-tr', '10', '10', '-te', str(bounds[0] - buffer), str(bounds[1] - buffer), str(bounds[2] + buffer), str(bounds[3] + buffer), in_shape, out_tiff])
        subprocess.run(cmd, shell=True)

    def merge(self, in_files, out_tiff):
        cmd = ' '.join(['gdal_merge.py', '-init', '0', '-n', '0', '-a_nodata', '0', '-o', out_tiff, ' '.join(in_files)])
        subprocess.run(cmd, shell=True)
