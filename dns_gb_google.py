#!/usr/bin/env python

import json
import csv
import urllib
import datetime
import time

now = int(time.time())
start_time = now - 86400 # 1 day
#start_time = now - 604800 # 1 week
#start_time = now - 2628000 # 1 Month
#start_time = now - 5256000 # 2 Months
#start_time = now - 7884000 # 3 Months
filename = "dns_results.csv"
url_prefix = "https://atlas.ripe.net/api/v1/measurement/"
url_suffix = "/result/?start=%s&stop=%s&format=json" % (start_time, now)
probe_url = "https://atlas.ripe.net/api/v1/probe/"
ASNs = {'AS5607':['Sky','3363831'],'AS2856':['BT','2348122'],'AS5089': ['Virgin Media','2347676'],'AS13285':['TalkTalk','2347678'],'AS20712':['Andrews & Arnold','2348128']}
ignore_recursors = ['8.8.8.8','8.8.4.4','208.67.222.222','208.67.222.220']

results = {}

for ISP in ASNs:
    isp_index = 0
    url = url_prefix + str(ASNs[ISP][1]) + url_suffix
    response = urllib.urlopen(url)
    data = json.load(response)
    AS = {}
    probe_data = {}

    for measurement in data:
        # Fetch probe details
        probe_id = str(measurement['prb_id'])
        if probe_id in probe_data:
            pass
        else:
            probe_url2 = probe_url + probe_id + "/"
            probe_response = urllib.urlopen(probe_url2)
            probe_data[probe_id] = json.load(probe_response)

        probe_asn = probe_data[probe_id]['asn_v4']

        # Probe IP Address
        probe_ip = measurement['from']

        # Generate rounded timestamp from measurement Unix time
        timestamp = datetime.datetime.fromtimestamp(measurement['timestamp']).strftime('%Y%m%d%H00')
        # Initialise dictionary per timestamp if non-existent
        if not AS.get(timestamp):
            AS[timestamp] = {}
        # Response Time, handle exceptions for failed measurements
        try:
            response_time = measurement['resultset'][0]['result']['rt']
        except KeyError:
            pass
        # Fetch Recursor Address
        try:
            recursor = measurement['resultset'][0]['dst_addr']
        except KeyError:
            pass

        # Check to see if the recursor is excluded
        if recursor in ignore_recursors: continue
        # Check to see if the probe has moved ASNs since allocation
        if int(probe_asn) != int(ISP[2:]):
            print("WARNING: Probe ID %s has moved from %s to AS%s. Ignoring value" % (probe_id, ISP, probe_asn))
            continue

        AS[timestamp][probe_id] = response_time

    #print "ASN : ProbeID : Timestamp : ResponseTime"
    for timestamp in AS:
        rt = 0
        count = 0
        for probe in AS[timestamp]:
            rt = rt + AS[timestamp][probe]
            count = count + 1
        rt = rt / count
        # Initialise dictionary per timestamp if non-existent
        if not results.get(timestamp):
            results[timestamp] = {}
        #Update dictionary of dictionaries
        results[timestamp][ISP] = rt

with open(filename, 'wb') as f:
##
## Write flattened list to CSV
    listASNs = ['Date']
    writer = csv.writer(f)
    for ASN in ASNs:
        name = ASN + " - " + ASNs[ASN][0]
        listASNs.append(name)
    writer.writerow(listASNs)

    for timestamp in sorted(results):
        row = [timestamp]
        for ASN in ASNs:
            try:
                row.append(results[timestamp][ASN])
            except KeyError:
                # Print a zero instead of null so we keep the output sane
                row.append("0")
        writer.writerow(row)


#print probe_asn, ",", timestamp, ",", probe_ip, ",", recursor, ",", response_time
