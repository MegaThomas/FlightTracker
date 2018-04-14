#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2017 chuanyi5 <chuanyi5@illinois.edu>
#
# Distributed under terms of the MIT license.

"""

"""
import requests as req
import datetime as dt
import json
import time
import gzip


def timer(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts))
        else:
            print(f'{method.__name__!r}  {(te - ts):.3f} s')
        return result
    return timed


def date_range(start_date: dt.date, end_date: dt.date, strf=None):
    for day in range(int((end_date - start_date).days)):
        if strf is not None:
            yield (start_date + dt.timedelta(days=day)).strftime(strf)
        else:
            yield start_date + dt.timedelta(days=day)


class Igola(object):
    def __init__(self):
        self.sess = req.session()
        self.site_res = self.sess.get("https://www.igola.com/flights/ZH/chi-bjs_2018-07-12*2018-08-11_1*RT*Economy_0*0")
        self.sess_res = None
        self.payload = {
            "lang": "EN",
            "enableMagic": True,
            "magicEnabled": True,
            "queryObj":
                {"tripType": "RT",
                 "item": [
                     {"from": {"c": "CHI", "t": "C"}, "to": {"c": "BJS", "t": "C"}, "date": "None"},
                     {"from": {"c": "BJS", "t": "C"}, "to": {"c": "CHI", "t": "C"}, "date": "None"}],
                 "passengerInfo": [],
                 "cabinType": "Economy",
                 "isDomesticCabinType": 0,
                 "cabinAlert": False}
        }

    def poll_payload(self):
        return {
            "currency": "CNY",
            "lang": "ZH",
            "sorters": [],
            "filters": [],
            "pageNumber": 1,
            "pageSize": 30,
            "sessionId": self.sess_res.json()["sessionId"]
        }

    def get_price(self, start_date: str, end_date: str) -> json:
        self.payload["queryObj"]["item"][0]["date"] = start_date
        self.payload["queryObj"]["item"][1]["date"] = end_date
        self.sess_res = self.sess.post("https://www.igola.com/web-gateway/api-flight-polling-data-hub/create-session",
                                       json=self.payload)
        poll_res = self.sess.post("https://www.igola.com/web-gateway/api-flight-polling-data-hub/packagedPolling",
                                  json=self.poll_payload())
        return poll_res.json()

    @timer
    def getter(self, start_start, start_end, end_start, end_end):
        start_dates = list(date_range(start_start, start_end, "%Y%m%d"))
        end_dates = list(date_range(end_start, end_end, "%Y%m%d"))
        # result_table = [[None]*len(end_dates)] * len(start_dates)
        result = {start: {end: None for end in date_range(end_start, end_end, "%Y%m%d")} for start in
                  date_range(start_start, start_end, "%Y%m%d")}
        for start in start_dates:
            for end in end_dates:
                result[start][end] = self.get_price(start, end)
        return result


if __name__ == '__main__':
    igola = Igola()
    start_start = dt.date(2018, 7, 11)
    start_end = dt.date(2018, 7, 19)
    end_start = dt.date(2018, 8, 8)
    end_end = dt.date(2018, 8, 16)

    result_table = igola.getter(start_start, start_end, end_start, end_end)

    file_path = f"./flight-ORD-PEK-{start_start.strftime('%Y%m%d')}-{end_end.strftime('%Y%m%d')}-" \
                f"{dt.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    # with open(file_path, 'a') as result_file:
    #     json.dump(result_table, result_file)
    with gzip.GzipFile(file_path, 'w') as fout:
        fout.write(json.dumps(result_table).encode('utf-8'))
