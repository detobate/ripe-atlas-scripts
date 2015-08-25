#!/usr/bin/env python

import json
import csv
import urllib
import datetime

filename = "/Users/rpa07/Code/ripeatlas/dns_results.csv"
url_prefix = "https://atlas.ripe.net/api/v1/measurement/"
url_suffix = "/result/?format=json"
probe_url = "https://atlas.ripe.net/api/v1/probe/"
ASNs = {'AS5607':['Sky','2347674'],'AS2856':['BT','2347716'],'AS5089': ['Virgin Media','2347676'],'AS13285':['TalkTalk','2347678'],'AS20712':['Andrews & Arnold','2347717']}
ignore_recursors = ['8.8.8.8','8.8.4.4','208.67.222.222','208.67.222.220']

results = {}

for ISP in ASNs:
    isp_index = 0
    url = url_prefix + str(ASNs[ISP][1]) + url_suffix
    response = urllib.urlopen(url)
    data = json.load(response)
    AS = {}

    for measurement in data:
        # Fetch source ASN for each probe
        probe_url2 = probe_url + str(measurement['prb_id']) + "/"
        probe_response = urllib.urlopen(probe_url2)
        probe_data = json.load(probe_response)
        probe_asn = probe_data['asn_v4']

        # Probe IP Address
        probe_ip = measurement['from']
        # Probe ID
        probe_id = measurement['prb_id']
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
            row.append(results[timestamp][ASN])
        writer.writerow(row)


#print probe_asn, ",", timestamp, ",", probe_ip, ",", recursor, ",", response_time
