import requests, re, sys, os
from bs4 import BeautifulSoup as bs
from datetime import time
from pydbus import SessionBus
import configparser as cp

bus = SessionBus()
notifications = bus.get('.Notifications')

class Gmail:
    def __init__(self, url_login, url_auth, url_mail, url_time, email, passwd):
        self.url_login = url_login
        self.url_auth = url_auth
        self.url_mail = url_mail
        self.url_time = url_time
        self.email = email
        self.passwd = passwd
        self.login()

    def login(self):
        self.ses = requests.session()
        try:
            login_html = self.ses.get(self.url_login)
        except:
            notifications.Notify('Gmail_notifier', 0, "", "", "No internet connection :(", [], {}, 5000)
            return
        soup = bs(login_html.content, 'html.parser').find('form').find_all('input')
        in_dict = {}
        for u in soup:
            if u.has_attr('value'):
                in_dict[u['name']] = u['value']
        in_dict['Email'] = self.email
        in_dict['Passwd'] = self.passwd
        self.ses.post(self.url_auth, data=in_dict)
        self.get_last_login_time()
    
    
    def get_last_login_time(self):
        login_info = self.ses.get(self.url_time)
        soup = bs(login_info.content, 'html.parser')
        soup = soup.find_all('td', text=re.compile("ago"))
        self.t = soup[1].text.split("(")[0].strip("").split()
        self.t = "".join(self.t)
        self.get_new_mails()


    def get_new_mails(self):
        self.a = []
        mail_list = self.ses.get(self.url_mail)
        soup = bs(mail_list.content, 'html.parser')
        soup = soup.find_all('table')[2].tr.find("table", attrs={'bgcolor': '#e8eef7'}).find_all("tr", attrs={'bgcolor': '#ffffff'})[0].find_all('td')
        for i in range(3, len(soup), 4):
            self.a.append("".join(soup[i].b.text.split("\xa0")))
        self.notify()

     
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
url_mail = "https://mail.google.com/mail/u/0/h/1iznvqv6mt7q7/?s=q&q=label%3Aunread&nvp_site_mail=Search%20Mail"
url_time = "https://mail.google.com/mail/u/0/h/qnsm1grq5h52/?&v=ac"


if __name__ == "__main__":
    config = cp.ConfigParser()
    config.read(os.path.join(sys.path[0], 'config.ini'))
    email = config[config.sections()[0]]['email']
    passwd = config[config.sections()[0]]['password']
    session = Gmail(url_login, url_auth, url_mail, url_time, email, passwd)