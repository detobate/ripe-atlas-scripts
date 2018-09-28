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
filename = '/home/detonate/public_html/dns_results.csv'
api_url = 'https://atlas.ripe.net/api/v2'
url_prefix = '/measurements/'
url_suffix = '/results/?start_time=%s&stop_time=%s' % (start_time, now)
probe_url = 'https://atlas.ripe.net/api/v2/probe/'
ASNs = {'AS5607':['Sky','16375685'],'AS2856':['BT','16375695'],'AS5089': ['Virgin Media','16375706'],
        'AS13285':['TalkTalk','16375914'],'AS20712':['Andrews & Arnold','16375740'],
        'AS13037': ['Zen Internet', '16388535'], 'AS56478': ['Hyperoptic', '16388541']}
ignore_recursors = ['8.8.8.8','8.8.4.4','208.67.222.222','208.67.222.220']
abnormal = 300 # ignore results that are abnormally high (in ms)


def get_probe_id(prb_id):
    url = api_url + '/probes/?id__in={}'.format(prb_id)
    response = urllib.urlopen(url)
    data = json.load(response)
    probe_asn = data['results'][0]['asn_v4']     # We should only ever receive 1 result, so idx on 0
    return(probe_asn)


def main():

    results = {}

    for ISP in ASNs:
        isp_index = 0
        url = api_url + url_prefix + str(ASNs[ISP][1]) + url_suffix
        response = urllib.urlopen(url)
        data = json.load(response)
        if 'error' in data:
            print('Failed to fetch data: {}'.format(data['error']))
            print(url)
            exit(1)

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

            probe_asn = get_probe_id(probe_id)
            #probe_asn = probe_data[probe_id]['asn_v4']

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
                # Skip results that are abnormally high
                if AS[timestamp][probe] > abnormal: continue
                rt = rt + AS[timestamp][probe]
                count = count + 1
            rt = rt / count
            print(rt)
            # Initialise dictionary per timestamp if non-existent
            if not results.get(timestamp):
                results[timestamp] = {}

            # Update dictionary of dictionaries
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
                    # Print a null string so Google Charts ignores it.
                    row.append('null')
            writer.writerow(row)


    #print probe_asn, ",", timestamp, ",", probe_ip, ",", recursor, ",", response_time


if __name__ == '__main__':
    main()