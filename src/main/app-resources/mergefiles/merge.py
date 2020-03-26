#!/opt/anaconda/envs/phenology/bin/python

# Merge phenology results
#
# This script can be used to merge the results from the crop phenology process to a single result
#
# Example usage: merge.py -i /tmp/input -o /tmp/output -f geojson -t /tmp/
# ---------------------------------------------------------
import os
import sys
import logging
from logging.config import fileConfig

import argparse
import datetime

sys.path.append('/opt/anaconda/envs/phenology/site-packages')
import geopandas as gpd
import json
import subprocess


# ---------------------------------------------------------
#                  Logging
# ---------------------------------------------------------

log = logging.getLogger()


# ---------------------------------------------------------
#                  Helper functions
# ---------------------------------------------------------

def mergeResults(features, format, out_dir, tmp_dir):
    features = [item for sublist in features for item in sublist]
    if format == 'geojson':
        data = {'type': 'FeatureCollection', 'features': features}
        writeToGeoJson(data, "{}/result.geojson".format(out_dir))
    elif format == "tif":
        for param in ["sos", "eos"]:
            createGeoTiff(features, param, out_dir, tmp_dir)


def createGeoTiff(features, param, out_dir, tmp_dir):
    out_file = "{}/{}.tif".format(out_dir, param)
    tmp_file = '{}/tmp_{}.shp'.format(tmp_dir, param)

    # Read in the features based on the phenology parameter
    features = list(map(lambda x: setProperty(x, param), features))
    gdp_data = gpd.GeoDataFrame.from_features(features)
    gdp_data.crs = {'init': 'epsg:4326'}
    gdp_data = gdp_data.to_crs({'init': 'epsg:3857'})
    bounds = gdp_data.total_bounds

    # Writhe the features to a temporary shapefile
    writeToShapeFile(gdp_data, tmp_file)

    # Rasterize the temporary shapefile
    buffer = 100
    cmd = ' '.join(['gdal_rasterize', '-a_nodata', '0', '-a', param, '-ot', 'UInt16', '-tr', '10', '10', '-te',
                    str(bounds[0] - buffer), str(bounds[1] - buffer), str(bounds[2] + buffer),
                    str(bounds[3] + buffer), tmp_file, out_file])
    subprocess.run(cmd, shell=True)

def setProperty(feature, param):
    new_feature = dict(feature)
    new_feature["properties"] = dict()
    new_feature["properties"][param] = datetime.datetime.strptime(feature["properties"][param]["time"], "%Y-%m-%d").timetuple().tm_yday
    return new_feature

def writeToGeoJson(data, output_file):
    with open(output_file, 'w') as output:
        output.write(json.dumps(data, indent=4))
        output.close()
        
def writeToShapeFile(features_gdf, output_file):
    features_gdf.to_file(output_file)

# ---------------------------------------------------------
#                  Argument parser
# ---------------------------------------------------------
parser = argparse.ArgumentParser(description='Calculate crop phenology based on input parameters')
parser.add_argument('-i', required=True, action='store', dest='input', help='Input directory')
parser.add_argument('-o', required=True, action='store', dest='output', help='Output directory')
parser.add_argument('-f', required=True, action='store', dest='format', help='Format of the output files')
parser.add_argument('-t', required=True, action='store', dest='temp',  help='Temp directory for intermediate files')

args = parser.parse_args()
geoms = list()

log.debug("Merging all files in {} in format {}".format(args.input, args.format))
merge_files = list()
for subdir, dirs, files in os.walk(args.input):
    for file in files:
        log.debug("Found {}/{} file for merging".format(subdir, file))
        with open(os.path.join(subdir, file), 'r') as data:
            merge_files.append(json.load(data))
log.debug("Found {} files to merge".format(len(merge_files)))
mergeResults(merge_files, args.format, args.output, args.temp)


