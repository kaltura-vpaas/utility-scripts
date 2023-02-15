from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.ElasticSearch import *

# Fill in the below three values appropriately
PARTNER_ID   = "xxxxxx"
ADMIN_SECRET = "yyyyyy"
USER_ID      = "zzzzzz"

config = KalturaConfiguration(PARTNER_ID)
config.serviceUrl = "https://www.kaltura.com/"

client = KalturaClient(config)
client.setClientTag("kmcng") # THIS IS IMPORTANT!
ks = client.generateSessionV2(
      ADMIN_SECRET,
      USER_ID,
      KalturaSessionType.ADMIN,
      PARTNER_ID,
      86400,
      "disableentitlement")
client.setKs(ks)

filter = KalturaMediaEntryFilter()
filter.mediaTypeIn = "1,5" # video and audio types
filter.advancedSearch = KalturaEntryCaptionAdvancedFilter()
filter.advancedSearch.hasCaption = KalturaNullableBoolean.TRUE_VALUE
pager = KalturaFilterPager()
result = client.baseEntry.list(filter, pager)

print("---------------------\nEntries with captions:\n---------------------")
for entry in result.objects:
      print(entry.id)
