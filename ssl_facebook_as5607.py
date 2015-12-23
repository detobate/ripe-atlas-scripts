#!/usr/bin/env python

import time
import datetime
import requests
import ujson
from ripe.atlas.sagan import SslResult

anomaly = 2000                  # How long is too long?
now = int(time.time())
start_time = now - 1209600      # 2 weeks
#start_time = now - 2628000      # 1 Month
#start_time = now - 7884000     # 3 Months
url_prefix = "https://atlas.ripe.net/api/v1/measurement/"
url_suffix = "/result/?start=%s&stop=%s&format=json" % (start_time, now)
probe_url = "https://atlas.ripe.net/api/v1/probe/"
measurements = {'IPv4':'2426343','IPv6':'2426342'}

resultsv4 = {}
resultsv6 = {}
countv4 = {}
countv6 = {}

for family in measurements:
    url = url_prefix + str(measurements[family]) + url_suffix
    response = requests.get(url)
    response = ujson.loads(response.text)

    for probe in response:
        # Catch failed results
        if 'dnserr' in probe:
            continue
        try:
            result = SslResult(probe)
        except:
            pass

        # Exclude anomalies
        if result.response_time is not None and result.response_time >= anomaly:
            break

        # We don't care about the minutes, collate all results in to the nearest hour
        roundedtime = result.created.strftime('%Y%m%d-%H00')


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
first = True
for time in sorted(resultsv4):
    if first is True:
        try:
            print("['%s', %s, %s]" % (time,(resultsv4[time] / countv4[time]),(resultsv6[time] / countv6[time])))
            first = False
        except:
            pass
    else:
        try:
            print(",\n['%s', %s, %s]" % (time,(resultsv4[time] / countv4[time]),(resultsv6[time] / countv6[time])))
            first = False
        except:
            pass
