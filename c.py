import requests
import json
import re


# base_url = 'http://lsgelection.kerala.gov.in/voters/view'
# r = requests.post(base_url, data={"value": 1})
# html = r.content.decode('utf-8')
# dist = []
# for i in range(1, 15):
#     dist.append(re.search('<option value=\"'+str(i)+'\"\>(.*?) \<\/option\>', html).group(1))
# print(dist)

# district_url = 'http://lsgelection.kerala.gov.in/getlocalbody'
# r = requests.post(district_url, data={"value": 1})
# d = json.loads(json.loads(r.content))["rData"]
# print(d[0]["lb_name"], d[0]["lb_code"])

# local_body_url = 'http://lsgelection.kerala.gov.in/getward'
# r = requests.post(local_body_url, data={"value": 339})
# d = json.loads(json.loads(r.content))["rData"]
# print(d[0]["ward_name"])

# polling_station_url = 'http://lsgelection.kerala.gov.in/getpollingstation'
# r = requests.post(polling_station_url, data={"value": 12130})
# d = json.loads(json.loads(r.content))["rData"]
# print(d[0]["gu_id"], d[0]["pol_station_name"])


