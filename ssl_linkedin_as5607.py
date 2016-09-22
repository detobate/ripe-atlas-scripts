#!/usr/bin/env python

import time
import requests
import ujson
from ripe.atlas.sagan import SslResult
import cgitb

anomaly = 1000                  # How long is too long?
now = int(time.time())
start_time = now - 1209600      # 2 weeks
#start_time = now - 2628000      # 1 Month
#start_time = now - 7884000     # 3 Months
url_prefix = "https://atlas.ripe.net/api/v2/measurements/"
url_suffix = "/results?start=%s&stop=%s&format=json" % (start_time, now)
probe_url = "https://atlas.ripe.net/api/v2/probe/"
measurements = {'IPv4':'5486845','IPv6':'5486844'}

header = ("<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01//EN' 'http://www.w3.org/TR/html4/strict.dtd'>\n"
          "<html lang='en'>\n<head>\n"
          "\t<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>\n"
          "\t<title>LinkedIn.com SSL Cert Fetch Times - AS5607</title>\n"
          "\t<script type='text/javascript' src='https://www.google.com/jsapi'></script>\n"
          "\t<script type='text/javascript'>\n"
          "\tgoogle.load('visualization', '1.1', {packages: ['line']});\n"
          "\tgoogle.setOnLoadCallback(drawChart);\n"
          "\n"
          "\tfunction drawChart() {\n"
          "\tvar data = new google.visualization.DataTable();\n"
          "\tdata.addColumn('string', 'Date');\n"
          "\tdata.addColumn('number', 'IPv4 Results in ms');\n"
          "\tdata.addColumn('number', 'IPv6 Results in ms');\n"
          "\tdata.addRows([\n")

footer = ("\t]);\n"
          "\tvar options = {\n"
          "\tchart: {\n"
          "\ttitle: 'Linkedin.com SSL Cert fetch time on AS5607',\n"
          "\tsubtitle: 'Average time in ms',\n"
          "\t},\n"
          "\twidth: 1180,\n"
          "\theight: 600,\n"
          "\thAxis: {\n"
          "\t}\n"
          "\t};\n"
          "\tvar chart = new google.charts.Line(document.getElementById('linechart_material'));\n"
          "\tchart.draw(data, google.charts.Line.convertOptions(options));\n"
          "\t}\n"
          "\t\t</script>\n"
          "\t</head>\n"
          "<body>\n"
          "\t<div id='linechart_material'></div>\n"
          "</body>\n</html>")

# Globals to keep track of results, even failed ones
countv4 = {}
countv6 = {}

def fetchResults():

    resultsv4 = {}
    resultsv6 = {}

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

            # Catch results with errors and skip to the next loop
            if result.is_error is True:
                #print("Probe: %s sucks because %s" % (result.probe_id, result.error_message))
                continue
            # Exclude anomalies
            if result.response_time is not None and result.response_time >= anomaly:
                continue

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

    return [resultsv4, resultsv6]

def parseResults(resultsv4, resultsv6):

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



def main():
    cgitb.enable()
    print("Content-Type: text/html;charset=utf-8\r\n\r\n")
    print(header)
    resultsv4, resultsv6 = fetchResults()
    parseResults(resultsv4, resultsv6)
    print(footer)

if __name__ == "__main__":
    main()