from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Schedule import *
from KalturaClient.exceptions import KalturaException
from csv import reader
import os

# Populate these with appropriate values
PARTNER_ID   = "xxxxxx"
ADMIN_SECRET = "xxxxxx"
USER_ID      = "test@user.com"
FROM_DATE    = 1619409600
TO_DATE      = 1619755200
INPUT_FILE   = "xxxxxx/liveEntries.csv"
OUTPUT_DIR   = "xxxxxx/Totals/"

reportTypeDict = {
    KalturaReportType.HIGHLIGHTS_WEBCAST:           'highlights.csv',         # 40001
    KalturaReportType.ENGAGEMENT_WEBCAST:           'engagement.csv',         # 40002
    KalturaReportType.QUALITY_WEBCAST:              'quality.csv',            # 40003
    KalturaReportType.ENGAGEMENT_BREAKDOWN_WEBCAST: 'engagementBreakdown.csv' # 40010
}

# Create the output directory if it does not exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Get a KalturaClient
config = KalturaConfiguration(PARTNER_ID)
config.serviceUrl = "https://www.kaltura.com/"
client = KalturaClient(config)
ks = client.session.start(
    ADMIN_SECRET,
    USER_ID,
    KalturaSessionType.ADMIN,
    PARTNER_ID,
    86400, # expiry
    "disableentitlement") # privileges
client.setKs(ks)

# open file in read mode
with open(INPUT_FILE, 'r') as readObj:

    # Iterate over each report type
    for reportType in reportTypeDict:
        # Create a new output file
        outputFile = open(OUTPUT_DIR + reportTypeDict[reportType], 'w')
        entryCount = 0
        print("Generating report: " + reportTypeDict[reportType] + " ...")

        # pass the file object to reader() to get the reader object
        readObj.seek(0) # offset to first line
        csvReader = reader(readObj)

        # Iterate over each row in the csv using reader object
        for row in csvReader:
            # row variable is a list that represents a row in csv
            entryId = row[0]

            try:
                reportInputFilter = KalturaReportInputFilter()
                reportInputFilter.entryIdIn = entryId
                reportInputFilter.fromDate = FROM_DATE
                reportInputFilter.toDate = TO_DATE
                pager = KalturaFilterPager()
                objectIds = ""
                responseOptions = KalturaReportResponseOptions()

                result = client.report.getTotal(reportType, reportInputFilter, objectIds, responseOptions)
                data = result.data

                # Only print header once
                if entryCount == 0:
                    print("EntryID," + result.header, file = outputFile)
                print("%s,%s" % (entryId, data), file = outputFile)
                entryCount += 1

            except KalturaException as e:
                print("Exception: %s", e.message)

        # close output file
        outputFile.close()