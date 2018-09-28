#!/usr/bin/env python3
import csv

file = '/Users/detonate/code/ripeatlas/ripe-atlas-scripts/dns_results.csv'

header = ("<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01//EN' 'http://www.w3.org/TR/html4/strict.dtd'>\n"
          "<html lang='en'>\n<head>\n"
          "\t<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>\n"
          "\t<title>Google.co.uk Recursive Query Resolve Time</title>\n"
          "\t<script type='text/javascript' src='https://www.gstatic.com/charts/loader.js'></script>\n"
          "\t<script type='text/javascript'>\n"
          "\tgoogle.charts.load('current', {packages: ['line']});\n"
          "\tgoogle.charts.setOnLoadCallback(drawChart);\n"
          "\n"
          "\tfunction drawChart() {\n"
          "\tvar data = new google.visualization.DataTable();\n")


footer = ("\tvar options = {\n"
          "\tchart: {\n"
          "\ttitle: 'Google.co.uk Resolve Time',\n"
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


def convert_datetime(timestamp):

    Y = timestamp[:4]
    M = timestamp[4:6]
    d = timestamp[6:8]
    h = timestamp[8:10]
    m = timestamp[10:12]

    datetime = (Y,M,d,h,m)
    return datetime


def main():

    line = 1
    csv_file = open(file)
    data = csv.reader(csv_file)
    entries = sum(1 for row in data)
    csv_file.seek(0)
    data = csv.reader(csv_file)

    output = []

    for row in data:
        if line == 1:
            output.append('\tdata.addColumn(\'datetime\', \'{}\');'.format(row[0]))
            for col in row[1:]:
                output.append('\tdata.addColumn(\'number\', \'{}\');'.format(col))

        elif line == 2:
            output.append('\tdata.addRows([')
            output.append('\t[new Date{}, {}],'.format(convert_datetime(row[0]), ','.join(row[1:])))
        elif line == entries:
            output.append('\t[new Date{}, {}]'.format(convert_datetime(row[0]), ','.join(row[1:])))
            output.append('\t]);\n')
        else:
            output.append('\t[new Date{}, {}],'.format(convert_datetime(row[0]), ','.join(row[1:])))

        line += 1

    output = header + '\n'.join(output) + footer
    return output

if __name__ == '__main__':
    print(main())


def application(env, start_response):
    status = '200 OK'
    header = ('Content-Type', 'text/html;charset=utf-8')
    output = main()
    output = ''.join(output)
    start_response(status, [header])
    return [bytes(output, 'utf-8')]

