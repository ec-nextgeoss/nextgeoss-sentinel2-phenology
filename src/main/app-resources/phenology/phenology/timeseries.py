import logging

import requests
import json
import pandas as pd
import datetime

from cropsar.service.api import get_cropsar_analysis
from shapely.geometry import Polygon

class TimeSeries:
    def getTimeSeries(self, geometry, start_date, end_date):
        if not start_date or not end_date:
            raise ValueError('Start and enddate are required')
        else:

            try:
                url = 'https://cropsar.vito.be/ts/CROPSAR/geometry?startDate=%s&endDate=%s' % (start_date, end_date)
                r = requests.post(url=url, json=geometry)
                if r.status_code != 200:
                    return None
                else:
                    data = r.json()['results']
                    return pd.DataFrame(data={'Times': map(lambda x: datetime.datetime.strptime(x['date'], "%Y-%m-%d"), data), 'Greenness': map(lambda x:x['result']['average'], data)})
            except:
                return None

    def calculateCropSAR(self, geometry, start_date, end_date, service='shub', layer='S2_FCOVER'):

        params = {
            'data_service': service,
            'model': 'RNNfull',
            'with_margin': True
        }

        field = Polygon(geometry.coordinates[0])

        data = self._getCropSARResult(get_cropsar_analysis(geometry=field, start=start_date, end=end_date, params=params, product=layer))
        return pd.DataFrame(data={'Times': list(map(lambda x: datetime.datetime.strptime(x['date'], "%Y-%m-%d"), data)), 'Greenness': list(map(lambda x:x['result']['average'], data))})

    def _getCropSARResult(self, ts):
        cropsar = ts['cropsar']

        results = []

        for date in sorted(cropsar.keys()):
            results.append({
                'date': date,
                'result': {
                    'average': float(cropsar[date]['q50']),
                    'lowerConfidence': float(cropsar[date]['q10']),
                    'upperConfidence': float(cropsar[date]['q90'])
                }
            })

        return results

    def smooth(self, timeseries, method=['Rolling Mean', 'SWETS'], window_size=10):
        smoothed = timeseries.copy()

        if method == 'Rolling Mean':
            smoothed.Greenness = timeseries.Greenness.rolling(window_size, center=True).mean()
        return smoothed
