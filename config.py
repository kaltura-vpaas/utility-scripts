from KalturaClient import *

PARTNER_ID   = "INSERT_PID"
ADMIN_SECRET = "INSERT_ADMIN_SECRET"
ADMIN_EMAIL  = "INSERT_ADMIN_EMAIL"
EXPIRY       = 86400

def getClient(userId, sessionType, expiry=EXPIRY, privileges=""):
    config = KalturaConfiguration(PARTNER_ID)
    config.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(config)

    ks = client.session.start(
        ADMIN_SECRET,
        userId,
        sessionType,
        PARTNER_ID,
        expiry,
        privileges)
    client.setKs(ks)
    return client
