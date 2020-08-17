from KalturaClient import *
from KalturaClient.Plugins.Core import *
import config

# Initialize vars
privileges        = "*"
partnerName       = "INSERT_CHILD_PARTNER_NAME" # Your own-system Account Name (string that will tell you which of your own customers this subaccount belongs to)
partnerEmail      = "INSERT_CHILD_PARTNER_EMAIL" # Your own-system customer login email (if your customers are to be allowed Admin access, otherwise this could something like AccountID@edcast.com)
partnerParentId   = config.PARTNER_ID # Your Kaltura Parent MultiAccount Partner ID (Kaltura Account ID)
templatePartnerId = 0 # VPaaS free trial template #Your Kaltura Template Account (This will be used to copy any template content or settings that should be uniformly applied to all of your sub-accounts).

# Get a KalturaClient
client = config.getClient("admin", KalturaSessionType.ADMIN, config.EXPIRY, privileges)

# Create partner
partner = KalturaPartner()
partner.adminEmail = partnerEmail
partner.adminName = partnerName
partner.name = partnerName
partner.type = KalturaPartnerType.ADMIN_CONSOLE
partner.partnerParentId = partnerParentId
#partner.referenceId = "some_reference_id" # Use this to store your own system Account ID (the id of the customer account in your own system), this is useful for reporting and search later
partner.description = partnerName + " child account."
partner.partnerPackage = 100
cmsPassword = ""
silent = False

result = client.partner.register(partner, cmsPassword, templatePartnerId, silent)
