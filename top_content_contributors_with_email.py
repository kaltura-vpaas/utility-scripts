from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.exceptions import KalturaException
from datetime import datetime
from time import strftime, localtime
from csv import reader

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# Initialize vars

TIME_ZONE_OFFSET = 240 # EST
REPORT_PAGE_SIZE = 500 # Will get first page only
PID = "ENTER_PID"
SECRET = "ENTER_ADMIN_SECRET"
USER_ID = "ENTER_USER_ID"

GATHER_YEARLY = False
if GATHER_YEARLY:
      YEAR = "2024"
      FROM_DAY = YEAR + "0101"
      TO_DAY = YEAR + "1231"
      OUTPUT_FILENAME = "./TopContentContributors/" + PID + "-" + YEAR + ".csv"
else:
      FROM_DAY = "20200101"
      TO_DAY = "20241231"
      OUTPUT_FILENAME = "./TopContentContributors/" + PID + ".csv"

# Initialize the KalturaClient
config = KalturaConfiguration()
config.serviceUrl = "https://cdnapisec.kaltura.com/"
client = KalturaClient(config)
ks = client.session.start(
      SECRET,
      USER_ID,
      KalturaSessionType.ADMIN,
      PID,
      86400,
      "disableentitlement")
client.setKs(ks)

# Get KMC users
filter = KalturaUserFilter()
filter.isAdminEqual = KalturaNullableBoolean.TRUE_VALUE
pager = KalturaFilterPager()
pager.pageSize = 500
result = client.user.list(filter, pager)

# Create dictionary of KMC users. Will want to output these if they arent in the report.
kmc_user_dict = dict()
for kmc_user in result.objects:
      kmc_user_dict[kmc_user.id] = kmc_user
      print(kmc_user.id, kmc_user.roleNames)

###################################################################################

report_type = KalturaReportType.TOP_CONTENT_CONTRIBUTORS
report_input_filter = KalturaEndUserReportInputFilter()
report_input_filter.interval = KalturaReportInterval.DAYS
report_input_filter.fromDay = FROM_DAY
report_input_filter.toDay = TO_DAY
#report_input_filter.fromDate = FROM_DATE
#report_input_filter.toDate = TO_DATE
report_input_filter.searchInAdminTags = False
report_input_filter.searchInTags = True
report_input_filter.timeZoneOffset = TIME_ZONE_OFFSET
pager = KalturaFilterPager()
pager.pageIndex = 1
pager.pageSize = REPORT_PAGE_SIZE
order = "-contributor_ranking"
#order = "-added_entries"
object_ids = ""
response_options = KalturaReportResponseOptions()
response_options.skipEmptyDates = False
result = client.report.getTable(report_type, report_input_filter, pager, order, object_ids, response_options)
print("Total records: %d" % result.totalCount)

# Split the data into one line per user
data = result.data
splitData = data[:-1]
splitData = data.replace(";", "\n")
splitData = splitData[:-2]

# Print the header of output file
outputFile = open(OUTPUT_FILENAME, "w")
print("User ID,Name,Email,User Created,KMC Role,KMC Last Login,Plays,Added Entries,Added Minutes,Ranking", file = outputFile)
#print(result.header, file = outputFile)
#print(result.header)

# Iterate over each user
for user_data in splitData.splitlines():
      #print("-------------")
      #print(user_data)

      # Split into 
      result = user_data.split(",")
      user_id = result[0]

      # Skip if user ID is not ascii or isn't empty string
      if is_ascii(user_id) and user_id != "" and user_id != "Unknown":
            # Check if valid user_id
            user_name = result[1]
            created_at = strftime('%Y-%m-%d %H:%M:%S', localtime(int(result[2])))
            plays = result[3]
            added_entries = result[4]
            added_minutes = float(result[5])/1000/60
            ranking = result[6]

            # Get this user's email address
            try:
                  kmc_role = ""
                  kmc_last_login = ""
                  kaltura_user = client.user.get(user_id)
                  email = kaltura_user.email

                  # Check if the user is a KMC user
                  if kaltura_user.isAdmin:
                        kmc_role = kaltura_user.roleNames
                        kmc_last_login = strftime('%Y-%m-%d %H:%M:%S', localtime(kaltura_user.lastLoginTime))

                        # remove this kmc admin user from the kmc_user_dict
                        if user_id in kmc_user_dict.keys():
                              del kmc_user_dict[user_id]

            except KalturaException as e:
                  email = "User no longer exists"
            print(user_id, email)
            print("%s,%s,%s,%s,%s,%s,%s,%s,%f,%s" % (user_id, user_name, email, created_at, kmc_role, kmc_last_login, plays, added_entries, added_minutes, ranking), file = outputFile)
      else:
            print("******", user_id, " : user is either empty string or not ascii-encoded unicode string")

# Output the KMC users which werent in the report
for user_id, kaltura_user in kmc_user_dict.items():
      if kaltura_user.lastLoginTime == None:
            last_login_time = "None"
      else:
            last_login_time = strftime('%Y-%m-%d %H:%M:%S', localtime(int(kaltura_user.lastLoginTime)))
      print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (user_id, kaltura_user.fullName, kaltura_user.email, strftime('%Y-%m-%d %H:%M:%S', localtime(int(kaltura_user.createdAt))), kaltura_user.roleNames, last_login_time, "", "", "", ""), file = outputFile)

outputFile.close()
