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
OUTPUT_DIR   = "xxxxxx/Tables/"

reportTypeDict = {
    KalturaReportType.MAP_OVERLAY_COUNTRY_WEBCAST: 'Country/', # 40004
    KalturaReportType.TOP_USERS_WEBCAST:           'Users/', # 40009
}

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
        print("Generating reports: " + reportTypeDict[reportType] + " ...")

        # Create the output directory if it does not exist
        outputDir = OUTPUT_DIR + reportTypeDict[reportType]
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        # pass the file object to reader() to get the reader object
        readObj.seek(0) # offset to first line
        csvReader = reader(readObj)

        # Iterate over each row in the csv using reader object
        for row in csvReader:
            # row variable is a list that represents a row in csv
            entryId = row[0]
            
            # Create a new output file for each live stream entry
            outputFile = open(outputDir + entryId + '.csv', 'w')

            try:
                reportInputFilter = KalturaEndUserReportInputFilter()
                reportInputFilter.entryIdIn = entryId
                reportInputFilter.fromDate = FROM_DATE
                reportInputFilter.toDate = TO_DATE
                pager = KalturaFilterPager()
                pager.pageIndex = 0
                pager.pageSize = 10000 # Max 10K Users - can adjust if needed
                order = ""
                objectIds = ""
                responseOptions = KalturaReportResponseOptions()

                result = client.report.getTable(reportType, reportInputFilter, pager, order, objectIds, responseOptions)
                data = result.data
                splitData = data.replace(";", "\n")
                print(result.header, file = outputFile)
                print(splitData, file = outputFile)

                # close output file
                outputFile.close()

            except KalturaException as e:
                print("Exception: %s", e.message)
