
# ---------------------------------------------------------
#                 Calculate phenology params
#
# This script can be used to calculate the start and end of season for all fields
# in a given shapefile. The result will be GeoTiff file containing the day of the year as a value.
#
# Example usage: calculate_phenology_params.py -sS "2018-04-02" -sE "2018-06-10" -mS "2018-06-10" -mE "2018-09-01" -eS "2018-09-01" -eE "2018-12-31" -sT 10.0 -eT 10.0 -i export.shp
# ---------------------------------------------------------

import sys
import logging
from logging.config import fileConfig

#sys.path.append('/opt/anaconda/envs/phenology3/site-packages')

import argparse
import datetime
import geojson
import json
from phenology.cropphenology import CropPhenology
from phenology.rasterizer import Rasterizer


# ---------------------------------------------------------
#                  Logging
# ---------------------------------------------------------

cropsar_logger = logging.getLogger('cropsar._retrieve')
cropsar_logger.setLevel(logging.DEBUG)

fileConfig('logging.conf')
log = logging.getLogger()



# ---------------------------------------------------------
#                  Argument parser
# ---------------------------------------------------------
parser = argparse.ArgumentParser(description='Calculate crop phenology based on input parameters')
parser.add_argument('-sS', required=True, action='store', dest='sStart', help='Start date of interval for start of season')
parser.add_argument('-sE', required=True, action='store', dest='sEnd', help='End date of tart interval for start of season')
parser.add_argument('-sT', required=True, action='store', dest='tSos', help='Threshold for start of season')
parser.add_argument('-mS', required=True, action='store', dest='mStart', help='Start date of interval for mid of season')
parser.add_argument('-mE', required=True, action='store', dest='mEnd', help='End date of tart interval for mid of season')
parser.add_argument('-eS', required=True, action='store', dest='eStart', help='Start date of interval for end of season')
parser.add_argument('-eE', required=True, action='store', dest='eEnd', help='End date of tart interval for end of season')
parser.add_argument('-eT', required=True, action='store', dest='tEos', help='Threshold for end of season')
parser.add_argument('-i', required=True, action='store', dest='input', help='Input geojson')
parser.add_argument('-o', required=True, action='store', dest='output', help='Output directory')

args = parser.parse_args()
geoms = list()

phenology = CropPhenology()

log.debug("Reading features from %s" % args.input)
with open(args.input) as json_file:
    features = json.load(json_file)

log.debug("Start processing of %d features" % len(features["features"]))

for index, feature in enumerate(features["features"]):
    log.debug("Processing field %d/%d" % (index + 1, len(features["features"])))
    geom_json = geojson.Feature(geometry=feature["geometry"], properties=feature["properties"]).geometry
    try:
        properties = feature["properties"]
        season_dates = phenology.extractSeasonDates(geom_json, args)
        properties.update(season_dates)
        if season_dates is None:
            log.error("Could not calculate phenology dates for field %s" % (index + 1))
        else:
            geoms.append({'type': 'Feature', 'geometry': geom_json, 'properties': properties})
    except:
        log.error(str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]))

if len(geoms) > 0:
    log.debug("Writing results to {}".format(args.output))
    phenology.writeResults(geoms, args.output, 'geojson')
else:
    log.debug("No succesfull fields!")
