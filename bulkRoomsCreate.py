from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Schedule import *
from KalturaClient.exceptions import KalturaException
from csv import reader
import config

# Initialize vars
userId = "kalturaTester"
sessionType = KalturaSessionType.ADMIN
expiry = 86400*30 # 30 days
kafEndpoint = "https://" + config.PARTNER_ID + ".kaf.kaltura.com/virtualEvent/launch"

# Get a KalturaClient
client = config.getClient(userId, sessionType, expiry)

# CSV format:
# roomName,roomDescription,Admin1FirstName,Admin1LastName,Admin2FirstName,Admin2LastName

# Header of output
print("Room Name,Description,Resource ID,Event ID,Admin 1 Display Name,Admin 1 Join URL,Admin 2 Display Name,Admin 2 Join URL")

# open file in read mode
with open('bulkRoomsIn.csv', 'r') as read_obj:
    next(read_obj) # skip first line / header

    # pass the file object to reader() to get the reader object
    csv_reader = reader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        # row variable is a list that represents a row in csv
        #print(row)
        rowLen = len(row)
        roomName    = row[0]
        roomDescrip = row[1]
        admin1First = row[2]
        admin1Last  = row[3]
        admin1Name  = "%s %s" % (admin1First, admin1Last)
        admin2First = row[4]
        admin2Last  = row[5]
        admin2Name  = "%s %s" % (admin2First, admin2Last)

        try:
            # Create resource
            resource = KalturaLocationScheduleResource()
            resource.description = roomDescrip
            resource.name = roomName
            resource.tags = "vcprovider:newrow,custom_rs_room_version:NR2"
            addResourceResult = client.schedule.scheduleResource.add(resource)
            resourceId = addResourceResult.id

            # Create event
            event = KalturaRecordScheduleEvent()
            event.startDate = 1596337740
            event.endDate = 1596424140
            event.recurrenceType = KalturaScheduleEventRecurrenceType.NONE
            event.summary = roomDescrip
            addEventResult = client.schedule.scheduleEvent.add(event)
            eventId = addEventResult.id

            # Create event resource
            eventResource = KalturaScheduleEventResource()
            eventResource.eventId = eventId
            eventResource.resourceId = resourceId
            addEventResourceResult = client.schedule.scheduleEventResource.add(eventResource)

            # Create Join URL for each of the two admins

            # Admin 1
            userId = "%s.%s@sdfc-kaltura.org" % (admin1First, admin1Last)
            privileges = "userContextualRole:1,role:viewerRole,eventId:%s,firstName:%s,lastName:%s" % (eventId, admin1First, admin1Last)
            ks = client.session.start(config.ADMIN_SECRET, userId, KalturaSessionType.USER, config.PARTNER_ID, expiry, privileges)
            admin1url = "%s?ks=%s" % (kafEndpoint, ks)

            # Admin 2
            userId = "%s.%s@sdfc-kaltura.org" % (admin2First, admin2Last)
            privileges = "userContextualRole:1,role:viewerRole,eventId:%s,firstName:%s,lastName:%s" % (eventId, admin2First, admin2Last)
            ks = client.session.start(config.ADMIN_SECRET, userId, KalturaSessionType.USER, config.PARTNER_ID, expiry, privileges)
            admin2url = "%s?ks=%s" % (kafEndpoint, ks)

            print("%s,%s,%s,%s,%s,%s,%s,%s" % (roomName, roomDescrip, resourceId, eventId, admin1Name, admin1url, admin2Name, admin2url))
            #print("\t%s" % admin1url)
            #print("\t%s" % admin2url)
            #print("-----------------------")

        except KalturaException as e:
            print("Exception: %s", e.message)
