from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Metadata import *
import datetime

# Populate these with appropriate values
PARTNER_ID   = "xxxxxx"
ADMIN_SECRET = "xxxxxx"
USER_ID      = "test@user.com"
RECIPIENT_EMAIL = "xxxxxx@xxx.xxx"  #The link to download the exported CSV file will be sent to this email address
FROM_DATE = int(datetime.datetime(2021, 6, 1, 0, 0).strftime('%s'))
TO_DATE = int(datetime.datetime(2021, 6, 30, 23, 59).strftime('%s'))
REPORT_MONTH = "2021_06"

# Initialize the KalturaClient
config = KalturaConfiguration()
config.serviceUrl = "https://cdnapisec.kaltura.com/"
client = KalturaClient(config)
ks = client.session.start(
      ADMIN_SECRET,
      USER_ID,
      KalturaSessionType.ADMIN,
      PARTNER_ID,
      86400,
      "disableentitlement")
client.setKs(ks)

params = KalturaReportExportParams()
params.recipientEmail = RECIPIENT_EMAIL
params.reportItems = []
params.reportItems.append(KalturaReportExportItem())
params.reportItems[0].reportType = KalturaReportType.USER_TOP_CONTENT
params.reportItems[0].action = KalturaReportExportItemType.TABLE
params.reportItems[0].order = "-count_plays"
params.reportItems[0].reportTitle = PARTNER_ID + "_" + REPORT_MONTH
params.reportItems[0].filter = KalturaEndUserReportInputFilter()
params.reportItems[0].filter.interval = KalturaReportInterval.DAYS
params.reportItems[0].filter.fromDate = FROM_DATE
params.reportItems[0].filter.toDate = TO_DATE
params.reportItems[0].filter.searchInAdminTags = False
params.reportItems[0].filter.searchInTags = True
params.reportItems[0].responseOptions = KalturaReportResponseOptions()
params.reportItems[0].responseOptions.skipEmptyDates = False

result = client.report.exportToCsv(params)