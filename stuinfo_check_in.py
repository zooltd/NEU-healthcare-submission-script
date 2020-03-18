import json
import requests
import os


class Checkin:
    def __init__(self, file_name="user_info.json"):
        with open(file_name, mode='r', encoding="utf-8") as f:
            stu_user = json.loads(f.read())
        self.stu_id = stu_user['stu_id']
        self.password = stu_user['password']
        self.s = requests.Session()
        self.header = {
            "Authorization": "Basic dnVlOnZ1ZQ==",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.122 Safari/537.36 "
        }

    def _oauth_login(self, url1="http://stuinfo.neu.edu.cn/api/auth/oauth/"):
        url1 = f"{url1}/token?username={self.stu_id}&grant_type=password&password={self.password}" \
               f"&imageCodeResult=&imageKey="
        access_info = self.s.post(url1, headers=self.header)
        access_info = json.loads(access_info.text)
        return access_info['token_type'], access_info['access_token']

    def _stu_login(self, url2="http://stuinfo.neu.edu.cn/cloud-xxbl/studenLogin"):
        token_type, access_token = self._oauth_login()
        self.header['Authorization'] = token_type + " " + access_token
        req_info = self.s.post(url2, headers=self.header)
        req_info = json.loads(req_info.text)
        return req_info['data']

    def _enter_check_in_page(self, url3="http://stuinfo.neu.edu.cn/cloud-xxbl/studentinfo?tag="):
        stu_tag = self._stu_login()
        url3 += stu_tag
        page_info = self.s.get(url3, headers=self.header)

    def _get_stu_info(self, url4="http://stuinfo.neu.edu.cn/cloud-xxbl/getStudentInfo"):
        self._enter_check_in_page()
        stu_info = self.s.get(url4, headers=self.header)
        stu_info = json.loads(stu_info.text)['data']
        return stu_info

    def _update_stu_info(self):
        with open("origin_data.json", 'r', encoding="utf-8") as f:
            origin_data = json.loads(f.read())
        stu_info = self._get_stu_info()
        for key in origin_data.keys():
            if key in stu_info:
                origin_data[key] = stu_info[key]
        with open("updated_data.json", 'w', encoding="utf-8") as f:
            f.write(json.dumps(origin_data, ensure_ascii=False))

    def submit(self, file_name="updated_data.json", url5="http://stuinfo.neu.edu.cn/cloud-xxbl/updateStudentInfo"):
        if not os.path.exists(file_name):
            self._update_stu_info()
        else:
            self._enter_check_in_page()
        with open(file_name, 'r', encoding="utf-8") as f:
            updated_data = json.loads(f.read())
        r = self.s.post(url5, data=json.dumps(updated_data), headers={"Content-Type": "application/json"})
        if (r.status_code == 200) and (json.loads(r.text)['success']):
            print('Success')
        else:
            print(r.status_code)
            print(r.text)


if __name__ == '__main__':
    checkin = Checkin()
    checkin.submit()
