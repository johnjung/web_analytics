# ab_testing

This is a placeholder for an AB testing script. For the time being it's just a
place to save the function for a two-tailed Fisher's exact test. In the future
I'd like to extend this by adding a web interface and other tests, like
chi-squared, or maybe tests for numeric data as well. 

The goal is to collect tests that deal with accepting support vs. rejecting 
support, and choose appropriate sample sizes (i.e. to know when I can stop
collecting data.)

## Contributing

Please contact the author with pull requests, bug reports, and feature
requests.

## Author

John Jung

# log_parsing

A script to regularize Apache log file data and Google Analytics data for an
instance of the VuFind library catalog software.

v. 0.0.1

## Parsing data with this script

Pipe either Google Analytics data or Apache log files into this script. It
outputs a tab-delimited data file that can be imported into Microsoft Excel. 

You will need to use different command-line switches on log_parsing.py to let
it know what whether data came from Apache log files or from Google Analytics, 
and you'll need to let it know what server it should parse data from. Right now
it's only set up to use VuFind data- I can add other data formats in the future. 

### Examples

#### Process Apache log files from Vufind

```
cat access_log | log_parsing --apache --vufind > vufind_apache_output.txt
```

#### Process Google Analytics data from VuFind
```
cat access_log | log_parsing --google --vufind > vufind_google_output.txt
```

## Getting data from Apache log files

Apache log files can be used as-is. You will need to copy them to your local
drive to pipe them into the Python script though. 

## Getting data from Google Analytics

Go to Behavior > Site Content > All Pages. 
Use the "Show rows" pulldown to show 5000 rows. 
Under the "Export" pulldown, select CSV. 

Confirm that the top of the file looks something like this:

```
# ----------------------------------------
# All Web Site Data
# Pages
# 20170526-20170601
# ----------------------------------------

Page,Pageviews,Unique Pageviews,Avg. Time on Page,Entrances,Bounce Rate,% Exit,Page Value
```

## Importing data into Excel

Go to File > Open.
Be sure "All Readable Documents" is selected in the Open dialog. 
Navigate to your file and click "Open". 

Step 1 of 3:
Under "Original data type" select the "Delimited" radio button. 
In the "File origin" pulldown, choose "Unicode". 
Click "Next". 

Step 2 of 3:
Under "Delimiters" check the "Tab" checkbox. 
Leave the "Treat consecutive delimiters as one" box unchecked.
Use the pulldown to select "{none}" as the text qualifier.
Click "Next".

Step 3 of 3:
Import every column as the text data format. (Selecting multiple columns at
once will be faster than doing them one at a time.) 
Click "Finish". 

## Contributing

Please contact the author with pull requests, bug reports, and feature
requests.

## Author

John Jung
