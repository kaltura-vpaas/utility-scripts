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
ks = client.generateSessionV2(
      ADMIN_SECRET,
      USER_ID,
      KalturaSessionType.ADMIN,
      PARTNER_ID,
      86400,
      "disableentitlement")
client.setKs(ks)

search_params = KalturaESearchEntryParams()
search_params.searchOperator = KalturaESearchEntryOperator()
search_params.searchOperator.operator = KalturaESearchOperatorType.AND_OP
search_params.searchOperator.searchItems = []
search_params.searchOperator.searchItems.append(KalturaESearchEntryItem())
search_params.searchOperator.searchItems[0].itemType = KalturaESearchItemType.EXISTS
search_params.searchOperator.searchItems[0].fieldName = KalturaESearchEntryFieldName.CAPTIONS_CONTENT
pager = KalturaPager()
result = client.elasticSearch.eSearch.searchEntry(search_params, pager)

print("---------------------\nEntries with captions:\n---------------------")
for entry in result.objects:
      print(entry.object.id)
