"""
    sStartDate: First date of the interval for getting season start
    sEndDate: Last date of the interval for getting season start

    mStartDate: First date of the interval for getting maximum greenness
    mEndDate: Last date of the interval for getting maximum greenness

    eStartDate: First date of the interval for getting season end
    eEndDate: Last date of the interval for getting season end

    tSos: The offset (%) to add to the start date minimum to set the start of the season
    tEos: The offset (%) to subtract from the end date minimum to set the end of the season
"""
import datetime
import json
import os

import pandas as pd
from phenology.timeseries import TimeSeries
from phenology.rasterizer import Rasterizer


class CropPhenology:

    def __init__(self):
        self.ts = TimeSeries()
        self.rasterizer = Rasterizer()
        self.params = ['sos', 'eos']

    def extractSeasonDates(self, geometry, args):

        result = {'sos': {'time': '', 'greenness': ''}, 'eos': {'time': '', 'greenness': ''}}

        timeseries = self.ts.calculateCropSAR(geometry, args.sStart, args.eEnd)

        if timeseries is None:
            return None
        else:
            timeseries = self.ts.smooth(timeseries, method='Rolling Mean')
            timeseries.dropna(inplace=True)

            # Get the local maximum greenness
            mMax = self.getLocalMax(timeseries, args.mStart, args.mEnd)
            dmMax = mMax['Times']
            ymMax = mMax['Greenness']

            # Get the start of season dates
            sos = self.getStartOfSeason(timeseries, args.sStart, args.sEnd, float(args.tSos), float(ymMax))
            result['sos']['time'] = sos[3].strftime('%Y-%m-%d')
            result['sos']['greenness'] = sos[2]

            # Get the end of season dates
            eos = self.getEndOfSeason(timeseries, args.eStart, args.eEnd, float(args.tEos), float(ymMax))
            result['eos']['time'] = eos[3].strftime('%Y-%m-%d')
            result['eos']['greenness'] = eos[2]

            return result

    def getLocalMax(self, df, start, end):
        df_range = df.loc[df['Times'].between(pd.Timestamp(start), pd.Timestamp(end))]
        return df_range.loc[df_range['Greenness'].idxmax()]

    """
        Calculate the start of the season based on selected interval [start, end] and a greenness curve (df). 
        Within this interval we will first look for the local minimum greenness, marked by (dsMin, ysMin). In the
        second step we will use the offset (%) to calculate the amount greenness offset that needs to be applied to 
        the minumum value in order to get the start of the season. This offset is calculated as a percentage of the 
        difference between the maximum greenness and the local minimum.
    """

    def getStartOfSeason(self, df, start, end, offset, yMax):
        # Get the local minimum greenness in the start season interval
        df_sRange = df.loc[df['Times'].between(pd.Timestamp(start), pd.Timestamp(end))]
        sMin = df_sRange.loc[df_sRange['Greenness'].idxmin()]
        dsMin = sMin['Times']
        ysMin = sMin['Greenness']

        # Calculate the greenness value corresponding to the start of the season
        ySos = ysMin + ((yMax - ysMin) * (offset / 100.0))

        # Get the closest value to this greenness
        df_sRange = df_sRange.loc[df_sRange['Times'] >= dsMin]
        sos = df_sRange.iloc[(df_sRange['Greenness'] - ySos).abs().argsort()[:1]]
        return (dsMin, ysMin, ySos, pd.to_datetime(str(sos['Times'].values[0])))

    """
        Calculate the end of the season based on selected interval [start, end] and a greenness curve (df). 
        Within this interval we will first look for the local minimum greenness, marked by (deMin, yeMin). In the
        second step we will use the offset (%) to calculate the amount greenness offset that needs to be applied to 
        the minumum value in order to get the start of the season. This offset is calculated as a percentage of the 
        difference between the maximum greenness and the local minimum.
    """

    def getEndOfSeason(self, df, start, end, offset, yMax):
        # Get the local minimum greenness in the start season interval
        df_eRange = df.loc[df['Times'].between(pd.Timestamp(start), pd.Timestamp(end))]
        eMin = df_eRange.loc[df_eRange['Greenness'].idxmin()]
        deMin = eMin['Times']
        yeMin = eMin['Greenness']

        # Calculate the greenness value corresponding to the start of the season
        yEos = yeMin + ((yMax - yeMin) * (offset / 100.0))

        # Get the closest value to this greenness
        df_eRange = df_eRange.loc[df_eRange['Times'] <= deMin]
        eos = df_eRange.iloc[(df_eRange['Greenness'] - yEos).abs().argsort()[:1]]
        return (deMin, yeMin, yEos, pd.to_datetime(str(eos['Times'].values[0])))

    """
        Function to write the output of the model to an output file. This is done by providing a geosjon of geometries
        containing the eos and sos properties  together with an output directory and an output format (shapefile, tiff 
        or geojson)
    """

    def writeResults(self, geoms, output_dir, format):
        if format == 'geojson':
            output_file = '{}.geojson'.format(output_dir)
            self._writeResultsGeoJson(geoms, output_file)
        elif format == 'tif' or format == 'shapefile':
            # Loop through the different crop phenology params
            for param in self.params:
                output_shp = '{}/{}.shp'.format(output_dir, param)

                # Write crop phenology results to a shapefile
                self._writeResultsShape(geoms, output_shp, param)

                # Create a tiff file
                if format == 'tif':
                    output_tiff = '{}/{}.tif'.format(output_dir, param)
                    self._createDirs(output_tiff)
                    self.rasterizer.rasterize(output_shp, output_tiff)

    """
        Helper function to write output to a geojson file
    """

    def _writeResultsGeoJson(self, geoms, output_file):
        self._createDirs(output_file)
        with open(output_file, 'w') as output:
            output.write(json.dumps(geoms, indent=4))
            output.close()

    """
        Helper function to write output to a shapefile
    """

    def _writeResultsShape(self, geoms, output_file, property):
        self._createDirs(output_file)
        self.rasterizer.writeToShapefile(output_file,
                                         list(map(
                                             lambda x: {'type': 'Feature', 'geometry': x['geometry'], 'properties': {
                                                 'value': datetime.datetime.strptime(
                                                     x['params']['season'][property]['time'],
                                                     "%Y-%m-%d").timetuple().tm_yday}},
                                             geoms)))

    """
        Function that will create the output path
    """
    def _createDirs(self, output_file):
        dir = os.path.dirname(output_file)
        if not os.path.exists(dir):
            os.makedirs(dir)