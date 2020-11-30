import requests
from math import ceil


class WFSReader:
    def __init__(self, url, layer):
        self.url = url
        self.layer = layer

    def getWFSFeatures(self, bbox, size=-1):
        url = "%s?service=WFS&request=GetFeature&version=1.1.0&typename=%s&outputFormat=application/json&srsname=EPSG:4326&bbox=%s,EPSG:4326" % (
            self.url, self.layer, ','.join(bbox))

        if size > 0:
            url += '&maxFeatures=%s' % size

        response = requests.get(url).json()
        return response['features']


    def getGroupedWFSFeatures(self, bbox, size=-1, groups=-1):
        features = self.getWFSFeatures(bbox, size)
        total = len(features)
        if int(groups) == -1:
            group_size = 1
        else:
            group_size = ceil(total / float(groups))
        groups = list()
        size_cnt = 1
        group_idx = 0
        groups.append(list())
        for feature in features:
            if size_cnt > group_size:
                size_cnt = 1
                group_idx += 1
                groups.append(list())
            groups[group_idx].append(feature["geometry"])
            size_cnt += 1
        return groups
