from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Schedule import *
from KalturaClient.exceptions import KalturaException

# Populate these with appropriate values
PARTNER_ID     = "XXXXX"
ADMIN_SECRET   = "YYYYY"
USER_ID        = "some@user.com"
TEMPLATE_ENTRY = "1_rlfsj3oi" # this is the template media entry used to create the recordings

# Get a KalturaClient
config = KalturaConfiguration(PARTNER_ID)
config.serviceUrl = "https://www.kaltura.com/"
client = KalturaClient(config)
ks = client.session.start(
    ADMIN_SECRET,
    USER_ID,
    KalturaSessionType.ADMIN,
    PARTNER_ID)
client.setKs(ks)

###########################
# Get list of media items with rootEntryId equal to the template media entry that is used for recording
filter = KalturaMediaEntryFilter()
filter.rootEntryIdEqual = TEMPLATE_ENTRY
pager = KalturaFilterPager()
result = client.media.list(filter, pager)
for x in result.objects:
    print("%s: %s" % (x.name, x.id))
