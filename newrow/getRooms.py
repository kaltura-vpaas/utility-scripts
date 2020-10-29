# This script outputs all rooms of a Newrow account.
# It implements the GET /rooms API.
# https://smart.newrow.com/backend/api/rooms/

import requests

page = 0
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': 'Bearer INSERT_TOKEN_HERE' }

# Print header
print("Room ID,Third Party ID,Room Name")

while True:
    url = 'https://smart.newrow.com/backend/api/rooms?page=%d' % page
    roomsResponse = requests.get(url, headers=headers)
    if roomsResponse.status_code == 200:
        roomsResponseJson = roomsResponse.json()
        #print roomsResponseJson['data']['next_page']
        #print roomsResponseJson['data']['total_count']
                
        # Get data for each room
        for room in roomsResponseJson['data']['rooms']:
            print(u"%s,%s,%s" % (room['id'], room['third_party_id'], room['name']))

        # Check if last page
        if roomsResponseJson['data']['next_page'] == "":
            break
        page += 1
