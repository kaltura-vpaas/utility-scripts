# This script outputs all quizzes associated to a Newrow room.
# It implements the GET /quizzes API.
# https://smart.newrow.com/backend/api/quizzes

import requests

page = 0
room_id = INSERT_ROOM_ID_HERE
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': 'Bearer INSERT_TOKEN_HERE' }

# Print header
print("Quiz ID,Room ID,Quiz Name")

while True:
    url = 'https://smart.newrow.com/backend/api/quizzes?page=%d&room_id=%d' % (page, room_id)
    quizzesResponse = requests.get(url, headers=headers)
    if quizzesResponse.status_code == 200:
        quizzesResponseJson = quizzesResponse.json()
        #print(quizzesResponseJson['data']['next_page'])
        #print(quizzesResponseJson['data']['total_count'])

        # Get data for each quiz
        for quiz in quizzesResponseJson['data']['quizzes']:
            print(u"%s,%s,%s" % (quiz['id'], quiz['room_id'], quiz['name']))

        # Check if last page
        if quizzesResponseJson['data']['next_page'] == "":
            break
        page += 1
