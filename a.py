import requests
import json
import re
import pytesseract
import cv2
import datetime
import csv
import os
import numpy as np

pytesseract.pytesseract.tesseract_cmd = 'D:\\git\\Tesseract-OCR\\tesseract.exe'

class VotersParser:
    def __init__(self, parent):
        self.par = parent
        self.directory = 'data'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def parse(self, voters, no):
        self.voters = voters
        # print (voters)
        self.len = len(voters)
        self.pos = 0

        self.remove_header("voters-list\">")
        with open('data/' + format(no, '06d') + '.csv', 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # iterate Voters
            self.nRows = 0
            while self.pos < self.len:
                if not self.remove("<tr>"):
                    break
                row_list = [no]
                # Parse Row
                isFinished = False

                # Check Next Item is <td>
                for i in range(7):
                    self.remove_space()
                    if self.voters[self.pos + 1] != 't' or self.voters[self.pos + 2] != 'd':
                        isFinished = True
                        break
                    self.remove("<td>")
                    if i == 0:
                        self.remove("<strong>")

                    item = self.read_content()
                    if i == 5:
                        row_list.append(item[0])
                        row_list.append(item[4:])
                    else :
                        row_list.append(item)

                    if i == 0:
                        self.remove("</strong>")
                    self.remove("</td>")
                if isFinished:
                    return
                # self.remove_td()

                # print(row_list)
                writer.writerow(row_list)
                # try:
                #     writer.writerow(row_list)
                # except:
                #     print('----------------->', row_list)
                self.nRows += 1
                if not self.remove("</tr>"):
                    return

    def remove(self, item):
        if not self.remove_space():
            return False
        self.pos += len(item)
        return True

    def remove_header(self, item):
        le = len(item)
        while self.pos < self.len:
            isOk = True
            for i in range(le):
                c = self.voters[self.pos + i]
                if c != item[i]:
                    isOk = False
                    break
            if isOk == True:
                self.pos += le
                return True
            self.pos += 1

    def remove_space(self):
        while self.pos < self.len:
            c = self.voters[self.pos]
            if c == ' ' or c == '\t' or c == '\n':
                self.pos += 1
                continue
            else:
                return True
        return False

    def read_content(self):
        ret = ''
        while self.pos < self.len and self.voters[self.pos] != '<':
            ret += self.voters[self.pos]
            self.pos += 1
        return ret

    def remove_td(self):
        while self.pos < self.len:
            if self.voters[self.pos] == 'd' and self.voters[self.pos + 1] == '>':
                self.pos += 2
                return
            self.pos += 1


class Scrap:

    def __init__(self):
        self.base_url = 'http://www.lsgelection.kerala.gov.in/voters/view'
        self.captcha_url = "http://www.lsgelection.kerala.gov.in/generate-captcha/_captcha_captcha"
        self.district_url = 'http://www.lsgelection.kerala.gov.in/public/getlocalbody'
        self.local_body_url = 'http://www.lsgelection.kerala.gov.in/public/getward'
        self.polling_station_url = 'http://www.lsgelection.kerala.gov.in/public/getpollingstation'

        self.session = requests.Session()
        r = self.session.get(self.base_url)
        # print(session.cookies.get_dict())
        self.cookie = "PHPSESSID={}; rufc=false".format(self.session.cookies.get_dict()['PHPSESSID'])
        # print(cookie)
        html = r.content.decode('utf-8')
        self.token = re.search('name=\"form\[\_token\]\" value=\"(.*?)\"', html).group(1)
        self.dist = []
        for i in range(1, 15):
            self.dist.append(re.search('<option value=\"'+str(i)+'\"\>(.*?) \<\/option\>', html).group(1))

        self.votersParser = VotersParser(self)
        if not os.path.isfile('index.csv'):
            with open('index.csv', 'w', newline='', encoding="utf-8") as index_file:
                index_writer = csv.writer(index_file)
                index_writer.writerow(['no', 'district_id', 'localBody_id', 'ward_id', 'pollingStation_id', 'district_name', 'localBody_name', 'ward_name', 'pollingStation_name','nRows'])

    def get_captcha(self):
        response = self.session.get(self.captcha_url, headers={'Cookie': self.cookie})
        # if response.status_code == 200:
        #     with open("sample.jpg", 'wb') as f:
        #         f.write(response.content)

        nparr = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # img = cv2.imread('sample.jpg')
        # captcha = pytesseract.image_to_string(img, lang='eng', config=" --psm 8")
        captcha = pytesseract.image_to_string(img, lang='eng',
                                              config=" --psm 7 -c tessedit_char_whitelist=abcdefghjklmnopqrstuvwxyzABCDEFGHJKLMNOPQRXYZ")
        #  -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz
        # captcha = (input("Input Prompting String: "))
        captcha = captcha.replace('\n', '')
        captcha = captcha.replace(' ', '')
        sumstr = ''
        cnt = 0
        for c in captcha:
            if c.isalpha():
                sumstr += c
                cnt += 1
            if cnt == 5:
                break
        captcha = sumstr
        # print(captcha)
        return captcha

    def scrap(self, cur, name, no):
        print('->', cur, no)
        while True:
            captcha = self.get_captcha()
            data = {
                "form[district]": cur[0],
                "form[localBody]": cur[1],
                "form[ward]": cur[2],
                "form[pollingStation]": cur[3],
                "form[language]": "E",
                "form[captcha]": captcha,
                "form[_token]": self.token,
            }

            r = self.session.post(self.base_url, data=data, headers={'Cookie': self.cookie})
            html = json.loads(r.content)["form"]

            # if r.status_code == 200:
            #     with open("out.html", 'w', encoding="utf-8") as f:
            #         f.write(html)

            # print(r.content)
            # html = r.content.decode('utf-8')
            if "DISTRICT:" in html:
                # print(datetime.datetime.now(), "OKOKOK")
                # with open("out.html", 'wb') as f:
                #     f.write(r.content)
                self.votersParser.parse(html, no)
                print(datetime.datetime.now(), 'nRows=', self.votersParser.nRows)
                with open('index.csv', 'a', newline='', encoding="utf-8") as index_file:
                    index_writer = csv.writer(index_file)
                    index_writer.writerow([no, cur[0], cur[1], cur[2], cur[3], name[0], name[1], name[2], name[3], self.votersParser.nRows])
                break
            else:
                print("Oh no!", captcha)

    def setStart(self, st, no):
        self.st = st
        self.no = no

    def setEnd(self, ed):
        self.ed = ed

    def start(self):
        cr = self.st
        self.name = ['', '', '', '']
        flag = True
        for s0 in range(self.st[0], self.ed[0] + 1):
            self.name[0] = self.dist[s0-1]

            r = self.session.post(self.district_url, data={"value": s0})
            d1 = json.loads(json.loads(r.content))["rData"]
            le1 = len(d1)
            for i in range(le1):
                s1 = int(d1[i]["id"])
                self.name[1] = d1[i]["lb_name"]
                if flag and s1 != self.st[1]:
                    continue

                r = self.session.post(self.local_body_url, data={"value": s1})
                d2 = json.loads(json.loads(r.content))["rData"]
                le2 = len(d2)
                for j in range(le2):
                    s2 = int(d2[j]["id"])
                    self.name[2] = d2[j]["ward_name"]
                    if flag and s2 != self.st[2]:
                        continue

                    r = self.session.post(self.polling_station_url, data={"value": s2})
                    d3 = json.loads(json.loads(r.content))["rData"]
                    le3 = len(d3)
                    for k in range(le3):
                        s3 = int(d3[k]["id"])
                        self.name[3] = d3[k]["pol_station_name"]
                        if flag and s3 != self.st[3]:
                            continue

                        flag = False
                        if [s0, s1, s2, s3] == self.ed:
                            return

                        self.scrap([s0, s1, s2, s3], self.name, self.no)
                        self.no += 1


if __name__ == "__main__":
    scrap = Scrap()
    # 1, 339, 12130, 33570
    # 14, 63, 7067, 35021

    scrap.setStart([1, 339, 12130, 33570], 1)
    # scrap.setStart([1, 340, 12143, 33587], 18)

    scrap.setEnd([14, 63, 7067, 35021])
    print(datetime.datetime.now(), '------------ The START ------------')
    scrap.start()
    print(datetime.datetime.now(), '------------ The END --------------')
    # url_district = 'http://lsgelection.kerala.gov.in/getlocalbody'
    # r = requests.post(url_district, data={"value":1})
    # d = json.loads(r.content)

    # url_local_body = 'http://lsgelection.kerala.gov.in/getward'
    # r = requests.post(url_local_body, data={"value":339})
    # d = json.loads(r.content)

    # url_polling_station = 'http://lsgelection.kerala.gov.in/getpollingstation'
    # r = requests.post(url_polling_station, data={"value":12130})
    # d = json.loads(r.content)



