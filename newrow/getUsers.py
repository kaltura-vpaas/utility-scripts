# This script outputs all users of a Newrow account.
# It implements the GET /users API.
# https://smart.newrow.com/backend/api/users/

import requests

page = 0
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': 'Bearer INSERT_TOKEN_HERE' }

# Print header
print("Newrow ID,Third Party ID,Email,First Name,Last Name,Role")

while True:
    url = 'https://smart.newrow.com/backend/api/users?page=%d' % page
    usersResponse = requests.get(url, headers=headers)
    if usersResponse.status_code == 200:
        usersResponseJson = usersResponse.json()
        #print usersResponseJson['data']['next_page']
        #print usersResponseJson['data']['total_count']
                
        # Get data for each user
        for user in usersResponseJson['data']['users']:
            print(u"%s,%s,%s,%s,%s,%s" % (user['id'], user['third_party_id'], user['email'], user['first_name'], user['last_name'], user['role']))

        # Check if last page
        if usersResponseJson['data']['next_page'] == "":
            break
        page += 1
