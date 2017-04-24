import requests, re, sys, os
from bs4 import BeautifulSoup as bs
from datetime import time
from pydbus import SessionBus

bus = SessionBus()
notifications = bus.get('.Notifications')

class Gmail:
    def __init__(self, url_login, url_auth, email, passwd):
        self.url_login = url_login
        self.url_auth = url_auth
        self.email = email
        self.passwd = passwd
        self.login()

    def login(self):
        self.ses = requests.session()
        login_html = self.ses.get(self.url_login)
        soup = bs(login_html.content, 'html.parser').find('form').find_all('input')
        in_dict = {}
        for u in soup:
            if u.has_attr('value'):
                in_dict[u['name']] = u['value']
        in_dict['Email'] = self.email
        in_dict['Passwd'] = self.passwd
        res = self.ses.post(self.url_auth, data=in_dict)
    
    
    def get_last_login_time(self, url):
        login_info = self.ses.get(url)
        soup = bs(login_info.content, 'html.parser')
        soup = soup.find_all('td', text=re.compile("ago"))
        self.t = soup[1].text.split("(")[0].strip("").split()
        self.t = "".join(self.t)
        return self.t


    def get_new_mails(self, url):
        self.a = []
        mail_list = self.ses.get(url)
        soup = bs(mail_list.content, 'html.parser')
        soup = soup.find_all('table')[2].tr.find("table", attrs={'bgcolor': '#e8eef7'}).find_all("tr", attrs={'bgcolor': '#ffffff'})[0].find_all('td')
        for i in range(3, len(soup), 4):
            self.a.append("".join(soup[i].b.text.split("\xa0")))
        return self.a

     
    def notify(self):
        cnt = 0
        if 'am' in self.t or 'pm' in self.t:
            s = self.t.split(":")
            dt = time(int(s[0]), int(s[1][:2]))
            if 'am' in self.t:
                for i in self.a:
                    if 'pm' in i:
                        cnt += 1
                    elif 'am' in i:
                        sp = i.split(":")
                        if dt < time(int(sp[0]), int(sp[1][:2])):
                            cnt += 1
                    else:
                        self.notify_show(cnt, 0)
                        break
            else:
                for i in self.a:
                    if 'pm' in i:
                        sp = i.split(":")
                        if dt < time(int(sp[0]), int(sp[1][:2])):
                            cnt += 1
                    else:
                        self.notify_show(cnt, 0)
                        break
        else:
            count1 = len(self.a[:self.a.index(self.t)])
            count2 = self.a.count(self.t)
            self.notify_show(count1, count2)


    def notify_show(self, c1, c2):
        icon = os.path.join(sys.path[0], 'Gmail.png')
        if c2 == 0:
            s = "You have %d new mails" % c1
            notifications.Notify('Gmail_notifier', 0, icon, "Gmail", s, [], {}, 5000)
        else:
            s = "You have %d new mails and %d unread mails from yesterday" % (c1, c2)
            notifications.Notify('Gmail_notifier', 0, icon, "Gmail", s, [], {}, 5000)

url_login = "https://accounts.google.com/ServiceLogin"
url_auth = "https://accounts.google.com/ServiceLoginAuth"
session = Gmail(url_login, url_auth, email, passwd)
session.get_new_mails("https://mail.google.com/mail/u/0/h/1iznvqv6mt7q7/?s=q&q=label%3Aunread&nvp_site_mail=Search%20Mail")
session.get_last_login_time("https://mail.google.com/mail/u/0/h/qnsm1grq5h52/?&v=ac")
session.notify()
