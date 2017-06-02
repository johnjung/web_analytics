#!/usr/local/bin/python

import csv, re, sys, urlparse

from optparse import OptionParser

# NOTES:
# looks like it's difficult to import tab-delimited data that contains UTF8 into Excel 2011 for Mac. 
# https://rothmanshore.com/2013/10/29/solved-editing-a-csv-with-utf-8-encoding-on-a-mac/

# TODO:
# Add importing for ArticlesPlus, the Database Finder, and EJournals.

####################
# GLOBAL VARIABLES #
####################

# regular expression for parsing Apache log files. 
regex = '^([^ ]+) - [^ ]+ \[(.*?)\] "(.*?)" (\d+) (\d+|-) "(.*?)" "(.*?)"$'

# if the current URL contains any of the following substrings, skip it.
skip_urls_containing = ['/vufind/AJAX/', '/vufind/Cart/', '/vufind/Cover/', '/vufind/Feedback/', '/vufind/MyResearch/', '/vufind/Record/', '/vufind/Search/Advanced', '/vufind/Search/FacetList', '/vufind/Search/OpenSearch', '/vufind/Search/Suggest', '/vufind/themes/']

# collect these filters. 
filter_headings = ['-author_facet', 'author_facet', '~author_facet', '-building', 'building', '~building', '-callnumber-first', 'callnumber-first', '~callnumber-first', '-format', 'format', '~format', '-language', 'language', '~language', '-series_facet', 'series_facet', '~series_facet', 'publishDate', '-topic_facet', 'topic_facet', '~topic_facet']

# collect these miscellaneous parameters. 
miscellaneous_headings = ['limit', 'page', 'sort']

# collect these sources.
source_headings = ['author', 'journal', 'lcc', 'series', 'title', 'topic']

# collect these types parameters. 
type_headings = ['AllFields', 'Author', 'Donor', 'JournalTitle', 'Notes', 'Performer', 'Publication Place', 'Publisher', 'Series', 'StandardNumbers', 'Subject', 'Title ', 'Title Uniform', 'Subject', 'toc', 'year', 'AuthorBrowse', 'LccBrowse', 'SeriesBrowse', 'TitleBrowse', 'TopicBrowse', 'ids', 'oclc_num']

# output these headings. 
headers = ['search type'] +  type_headings + source_headings + miscellaneous_headings + filter_headings + ['query string']

# FUNCTION DEFINITIONS

# parse a line of the apache log file. 
# return GETs that returned a 200 only. 
# returns None, or a string (the URL.)
def apache_log_line_to_request_path(line):
    try:
        log_fields = re.match(regex, line).groups()
    except AttributeError:
        print("Error when parsing: " + line)
        sys.exit()

    # e.g. 192.5.85.4
    ip_address = log_fields[0]

    # e.g. 26/May/2017:18:44:48 -500
    date_and_time = log_fields[1]

    # e.g. GET or POST
    request_verb = log_fields[2].split(' ')[0]

    # e.g. /bmrc/view.php?eadid=BMRC.SHOREFRONT.BLACKBOARD.SURVEY
    request_path = log_fields[2].split(' ')[1]

    # e.g. 200
    http_status_code = log_fields[3]

    # url that referred this one, or '-'. 
    referrer = log_fields[5]

    # e.g. 'gsa-crawler...'
    user_agent = log_fields[6]

    # GET requests only.
    if not request_verb == 'GET':
        return None

    # successful requests only. 
    if not http_status_code == '200':
        return None

    return request_path

# parse a line of CSV data exported from Google Analytics. 
# returns None, or a string (the URL.)
def google_analytics_export_line_to_request_path(line):
    request_path = line.split(',')[0]
    try:
        return request_path if request_path[0] == '/' else None
    except IndexError:
        return None

# for a VuFind URL, get the fields we want to export. 
# returns None if fields cannot be found, or a list of fields. 
def vufind_request_path_to_fields(request_path):
    # basic keyword, advanced keyword, or browse. 
    search_type = ''

    if (any(s in request_path for s in skip_urls_containing)):
        return None

    # a dictionary of url parameters
    parameters = urlparse.parse_qs(urlparse.urlparse(request_path).query)

    # query string.
    query_string = ''
    if '?' in request_path:
        query_string = request_path.split('?', 1)[1]

    # collect filters. 
    filters = dict.fromkeys(filter_headings, '')

    if 'filter[]' in parameters:
        for f in parameters['filter[]']:
            filters[f.split(':')[0]] = f.split(':', 1)[1]

    # collect miscellaneous URL parameters.
    miscellaneous = dict.fromkeys(miscellaneous_headings, '')
    for p in miscellaneous:
        if p in parameters:
            miscellaneous[p] = parameters[p][0]

    # basic and advanced search fields
    types = dict.fromkeys(type_headings, '')

    if '/vufind/Search/Results' in request_path:
        # basic search
        if 'lookfor' in parameters:
            search_type = 'basic keyword'
            if not 'type' in parameters:
                types['AllFields'] = parameters['lookfor'][0]
            else:
                for t in types.keys():
                    if t == parameters['type'][0]:
                        types[t] = parameters['lookfor'][0]

        # advanced search
        for lookfor_n, type_n in (('lookfor0[]', 'type0[]'), ('lookfor1[]', 'type1[]'), ('lookfor2[]', 'type2[]')):
            if lookfor_n in parameters and type_n in parameters:
                search_type = 'advanced keyword'
                for l, t in zip(parameters[lookfor_n], parameters[type_n]):
                    types[t] = l

    # browses
    sources = dict.fromkeys(source_headings, '')

    if '/vufind/Alphabrowse' in request_path or '/vufind/alphabrowse' in request_path:
        if 'from' in parameters and 'source' in parameters:
            search_type = 'browse'
            sources[parameters['source'][0]] = parameters['from'][0]

    fields = [search_type] +  [types[t] for t in type_headings] + [sources[s] for s in source_headings] + [miscellaneous[m] for m in miscellaneous_headings] + [filters[f] for f in filter_headings] + [query_string]

    return fields

########
# MAIN #
########

# parse command line options. 
parser = OptionParser()
parser.add_option("-a", "--apache", action="store_true", dest="apache", default=False)
parser.add_option("-g", "--google", action="store_true", dest="google", default=False)
parser.add_option("-v", "--vufind", action="store_true", dest="vufind", default=False)
(options, args) = parser.parse_args()

if not options.apache and not options.google:
    sys.stderr.write("You must enter an export type, either --apache or --google.")
    sys.exit()

if not options.vufind:
    sys.stderr.write("You must enter a data type, either --vufind, or...")
    sys.exit()

# write headers.
csv_writer = csv.writer(sys.stdout, delimiter="\t", quotechar="\\", quoting=csv.QUOTE_MINIMAL)
csv_writer.writerow(headers)

# loop over input. 
while True:
    line = sys.stdin.readline()
    if line == '':
        break
        
    # get the request path from server data. 
    request_path = None
    if options.apache:
        request_path = apache_log_line_to_request_path(line)
    elif options.google:
        request_path = google_analytics_export_line_to_request_path(line)

    if request_path == None:
        continue

    # get output fields from the request path.
    fields = None
    if options.vufind:
        fields = vufind_request_path_to_fields(request_path)
        
    if fields == None:
        continue

    csv_writer.writerow(fields)

