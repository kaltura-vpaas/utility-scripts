from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Schedule import *
from KalturaClient.exceptions import KalturaException
from csv import reader
from datetime import datetime
import webbrowser

# Populate these with appropriate values
PARTNER_ID   = "XXXXX"
ADMIN_SECRET = "YYYYY"
USER_ID      = "some@user.com"

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
# (1) Create Media Template Entry: this media entry will be cloned for each recording
# Alternatively, can use existing media entry.
entry = KalturaMediaEntry()
entry.mediaType = KalturaMediaType.VIDEO
entry.name = "Media Entry For Recording"
mediaEntryResult = client.media.add(entry)
print("%s: %s" % (mediaEntryResult.name, mediaEntryResult.id))

###########################
# (2) Create Schedule Resource (the virtual room)
# Alternatively, can use existing room.
schedule_resource = KalturaLocationScheduleResource()
schedule_resource.description = "A sample room"
schedule_resource.name = "Sample Room"
schedule_resource.tags = "vcprovider:newrow"
resourceResult = client.schedule.scheduleResource.add(schedule_resource)
print("%s: %s" % (resourceResult.name, resourceResult.id))

###########################
# (3) Create Schedule Event (an event scheduled to take place in the virtual room)
schedule_event = KalturaRecordScheduleEvent()
schedule_event.templateEntryId = mediaEntryResult.id # set to Media Entry ID
schedule_event.startDate = 1620155880
schedule_event.endDate = 1620157200
schedule_event.recurrenceType = KalturaScheduleEventRecurrenceType.NONE
schedule_event.summary = "Some event"
eventResult = client.schedule.scheduleEvent.add(schedule_event)
print("%s: %s" % (eventResult.summary, eventResult.id))

###########################
# (4) Create Schedule Event Resource - linking the event to the resource
schedule_event_resource = KalturaScheduleEventResource()
schedule_event_resource.eventId = eventResult.id
schedule_event_resource.resourceId = resourceResult.id
eventResourceResult = client.schedule.scheduleEventResource.add(schedule_event_resource)
print("Event %s linked to Resource %s" % (eventResourceResult.eventId, eventResourceResult.resourceId))

###########################
# (5) Launch room
privileges = "userContextualRole:0,role:adminRole,firstName:Jon,lastName:Doe,eventId:%s" % eventResult.id
joinSession = client.session.start(ADMIN_SECRET, USER_ID, KalturaSessionType.USER, PARTNER_ID, 86400, privileges)
url = 'https://%s.kaf.kaltura.com/virtualEvent/launch?ks=%s' % (PARTNER_ID, joinSession)
webbrowser.open_new(url)