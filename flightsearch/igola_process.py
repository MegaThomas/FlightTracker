#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2017 chuanyi5 <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""
Find price patterns in igola flight data
"""
from flightsearch import igola
import gzip
import json
import os
import re
from collections import OrderedDict
import pandas as pd
import numpy as np


class Pattern(object):
    def __init__(self, results: OrderedDict):
        num_fetches = len(results)
        self.fetch_time = [None] * num_fetches
        first = price[list(price)[0]]
        self.start_dates = np.sort(np.array(list(first)).astype(int))
        self.end_dates = np.sort(np.array(list(first[str(self.start_dates[0])])).astype(int))
        num_start, num_end = len(self.start_dates), len(self.end_dates)
        self.lowest_nonstop = np.empty([num_fetches, num_start, num_end])
        self.lowest_onestop = np.empty([num_fetches, num_start, num_end])
        self.low_airlines = np.empty([num_fetches, num_start, num_end])

        for idx_fetch, (fetch_time, result) in enumerate(results.items()):
            self.fetch_time[idx_fetch] = fetch_time
            for start_date, start_dict in result.items():
                for end_date, price_info in start_dict.items():
                    idx_start = np.where(int(start_date) == self.start_dates)[0]
                    idx_end = np.where(int(end_date) == self.end_dates)[0]
                    self.lowest_nonstop[idx_fetch, idx_start, idx_end] = price_info['stopInfo'][0]['lowestPrice']
                    self.lowest_onestop[idx_fetch, idx_start, idx_end] = price_info['stopInfo'][1]['lowestPrice']


if __name__ == '__main__':
    file_pattern = re.compile(r'flight-(\w+)-(\w+)-(\d+)-(\d+)-(\d+).json.gzip')
    price = OrderedDict()
    threshold = 8000
    for file in os.listdir("./"):
        ma = file_pattern.match(file)
        if ma is not None:
            with gzip.GzipFile(file, 'r') as fin:
                price.update({ma.group(5): json.loads(fin.read().decode('utf-8'))})

    pattern_table = Pattern(price)
    # for fetch_time, result in iteritems(price):
    #     pattern_table.push(
    #         fetch_time,
    #         result['stopinfo'][0]['lowestPrice'],
    #         result['stopinfo'][1]['lowestPrice'],
    #         [airline for airline in result['airlineInfo'] if airline['lowestPrice'] <= threshold])

    print("check")
    # file_path = ""
    # with gzip.GzipFile(file_path, 'r') as fin:
    #     json.loads(fin.read().decode('utf-8'))
