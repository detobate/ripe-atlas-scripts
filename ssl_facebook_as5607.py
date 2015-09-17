#!/usr/bin/env python

import urllib
import datetime
import requests
from ripe.atlas.sagan import SslResult

url_prefix = "https://atlas.ripe.net/api/v1/measurement/"
url_suffix = "/result/?format=json"
probe_url = "https://atlas.ripe.net/api/v1/probe/"
measurements = {'IPv4':'2426343','IPv6':'2426342'}

resultsv4 = {}
resultsv6 = {}
countv4 = {}
countv6 = {}

for family in measurements:
    url = url_prefix + str(measurements[family]) + url_suffix
    response = requests.get(url).json()

    for probe in response:
        # Catch failed results
        if 'dnserr' in probe:
            continue
        try:
            result = SslResult(probe)
        except:
            pass
        # We don't care about the minutes, collate all results in to the nearest hour
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

# Output stuff here.  Munge in to Google graphing API.
for time in sorted(resultsv4):
    print "Average IPv4 response time: ", time, ":", (resultsv4[time] / countv4[time])

for time in sorted(resultsv6):
    print "Average IPv6 response time: ", time, ":", (resultsv6[time] / countv6[time])
