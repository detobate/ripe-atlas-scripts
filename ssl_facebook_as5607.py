#!/usr/bin/env python

import urllib
import datetime
import requests
from ripe.atlas.sagan import SslResult

filename = "/Users/rpa07/Code/ripeatlas/ssl_facebookv4.csv"
url_prefix = "https://atlas.ripe.net/api/v1/measurement/"
url_suffix = "/result/?format=json"
probe_url = "https://atlas.ripe.net/api/v1/probe/"
measurements = {'IPv4':'2417352','IPv6':'2417351'}

resultsv4 = {}
resultsv6 = {}
countv4 = {}
countv6 = {}

for family in measurements:
    url = url_prefix + str(measurements[family]) + url_suffix
    response = requests.get(url).json()

    for probe in response:
        if 'dnserr' in probe:
            break
        try:
            result = SslResult(probe)
        except:
            pass
        roundedtime = result.created.format('YYYYMMDD-HH00')

        if family == 'IPv4':
            if roundedtime in resultsv4:
                try:
                    updated_time = result.response_time + resultsv4[roundedtime]
                    resultsv4.update({roundedtime: updated_time})
                except:
                    pass
            else:
                resultsv4.update({roundedtime: result.response_time})
            if roundedtime in countv4:
                countv4[roundedtime] = countv4[roundedtime] + 1
            else:
                countv4[roundedtime] = 1

        elif family == 'IPv6':
            if roundedtime in resultsv6:
                try:
                    updated_time = result.response_time + resultsv6[roundedtime]
                    resultsv6.update({roundedtime: updated_time})
                except:
                    pass
            else:
                resultsv6.update({roundedtime: result.response_time})
            if roundedtime in countv6:
                countv6[roundedtime] = countv6[roundedtime] + 1
            else:
                countv6[roundedtime] = 1

for time in sorted(resultsv4):
    print "Average IPv4 response time: ", time, ":", (resultsv4[time] / countv4[time])

for time in sorted(resultsv6):
    print "Average IPv6 response time: ", time, ":", (resultsv6[time] / countv6[time])
