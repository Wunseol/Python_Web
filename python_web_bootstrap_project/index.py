#coding=utf-8
import calendar
import hashlib

import pymysql
import requests
import web
from bs4 import BeautifulSoup
import urllib.request
import json
import time

urls=(
    '/login.html','login',
    '/', 'index',
    '/calendar.html','rili',
    '/fanyi.html','fanyi',
    '/resume.html','resume',
    '/lol.html', 'lol',
    '/cashbox.html','cashbox',
    '/weather.html','weather',
    '/workers.html','workers',
    '/books.html','books',
    '/tongcheng.html','tongcheng',
    '/students','students',

)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
}

# 链接mysql

def sqlSelect(sql):
    conn=pymysql.connect(host='localhost',port=3306,user='root',passwd='nhcwc',db='web')
    cur = conn.cursor()
    cur.execute(sql)
    sqlData=cur.fetchall()
    cur.close()
    conn.close()
    return sqlData


def sqlWrite(sql):
    conn=pymysql.connect(host='localhost',port=3306,user='root',passwd='nhcwc',db='web')
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
    return


class login:
    def GET(self):
        return render.login("")

    def POST(self):
        webData = web.input()
        username = webData.get("username")
        password = webData.get("password")
        #计算密码的md5值
        m = hashlib.md5()
        m.update(password.encode("utf-8"))
        password = m.hexdigest()

        sql = "select name from user where username ='%s' and password='%s'"%(username,password)
        sqlData = sqlSelect(sql)
        if len(sqlData)==0:
            return render.login("密码错误")
        else:
            session.username = username
            session.name = sqlData[0][0]
            print(session.name)
            raise web.seeother('/')

        
class index:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            return render.index(session.name)

        
class lol:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            notice = ""
            return render.lol("敖兴",['','','','','','',''],notice)

    def POST(self):

        webData = web.input()
        query = webData.get("query")

        sql = "select tftid,displayname,races,skillname,attackdata,lifedata,skillintroduce from lol where displayname='%s'"%query
        sqlData = sqlSelect(sql)
        
        if len(sqlData)==0:
            notice ="Not Found"
            sqlData = ['','','','','','','']
        else:
            notice = ""
            sqlData = sqlData[0]

        print(notice,sqlData)
        
        return render.lol(query,sqlData,notice)


class resume:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            return render.resume()
    
    
class rili:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            return render.riliWeb("2022","12",calendar.month(2022,12))
    
    def POST(self):
        webData = web.input()
        year = webData.get("yearInput","2022")
        month = webData.get("monthInput","12")
        data = calendar.month(int(year),int(month))
        return render.riliWeb(year,month,data)


class fanyi:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            q = "Python"
            explainList = [
                [1,"n. 巨蟒；大蟒；丹舌; n. （Python）人名；（法）皮东"],
                [2,"n. 蟒蛇（python 的复数）"],
                [3,"adj. 预言的；神谕的；大蟒似的"],
                [4,"n. 女预言家；女巫；古希腊德尔菲的太阳神殿的女祭司"],
                [5,"adj. 皮东风格的；搞笑的；奇怪的"]
            ]
            flag = 1
            return render.youdao(q,explainList,flag)
        
    def POST(self):
        webData = web.input()
        q = webData.get("q")
        if "search" in webData:
            url = "https://dict.youdao.com/suggest?num=5&ver=3.0&doctype=json&cache=false&le=en&q="+q
            response = requests.get(url)
            data = response.json()

            explainList = []
            i = 1
            s = ""
            for t in data["data"]["entries"]:
                explainList.append([i,t["explain"]])
                s += t["explain"]
                i+=1
            if s=="":
                s = "Fail"
            sql = "insert into history(username,query,result) values('%s','%s','%s')"%(session.username,q,s)
            sqlWrite(sql)
            flag =1
            return render.youdao(q,explainList,flag)
        else:
            sql = "select history.time,user.name,query,result from history,user where history.username=user.username"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.youdao(q,sqlData,flag)


class cashbox:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            logid="输入logid"
            logdata ="2022-12-3"
            lognote = "shopping"
            charge = "-200"
            balance = "300"
            data=""
            flag = 1
            return render.cashbox(logid,logdata,lognote,charge,balance,data,flag)

    def POST(self):
        
        webData = web.input()
        logid = webData.get("logid")
        logdata = webData.get("logdata")
        lognote = webData.get("lognote")
        charge = webData.get("charge")
        balance = webData.get("balance")
        if "search" in webData:
            sql = "insert into cashbox(logdata,lognote,charge,balance) values('%s','%s','%s','%s')"%(logdata,lognote,charge,balance)
            sqlWrite(sql)
            sql = "select id,logdata,lognote,charge,balance from cashbox"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.cashbox(logid,logdata,lognote,charge,balance,sqlData,flag)
        if "delete" in webData:
            sql = "delete from cashbox where id='%s'"%(logid)
            sqlWrite(sql)
            sql = "select id,logdata,lognote,charge,balance from cashbox"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.cashbox(logid,logdata,lognote,charge,balance,sqlData,flag)

        if "history" in webData:
            sql = "select id,logdata,lognote,charge,balance from cashbox"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.cashbox(logid,logdata,lognote,charge,balance,sqlData,flag)
  

class weather:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            cityname = "上海"
            data=""
            flag = 1
            return render.weather(cityname,data,flag)
        
    def POST(self):
        webData = web.input()
        cityname = webData.get("cityname")
        if "search" in webData:
                
            host = 'http://api.k780.com:88/?app=weather.future&weaid=%s'%cityname
            url = host+'&appkey=10003&sign=b59bc3ef6191eb9f747dd4e83c99f2a4&format=xml'
            # 官方网站：http://www.k780.com
            # 说明：数据来自国家气象局天气网,每小时更新一次    
            # 免费版有每小时点击次数的限制（免费版最多每小时72000次查询）
            
            response = requests.get(url)
            content = response.text
            soup = BeautifulSoup(content,'lxml')

            #日期
            day = []
            target=soup.find_all('days')
            for each in target:
                day.append(each.text)
            #星期
            week=[]
            target=soup.find_all('week')
            for each in target:
                week.append(each.text)
            #城市
            city=[]
            target=soup.find_all('citynm')
            for each in target:
                city.append(each.text)
            #温度
            temperature=[]
            target=soup.find_all('temperature')
            for each in target:
                temperature.append(each.text)
            #天气状况
            weather=[]
            target=soup.find_all('weather')
            for each in target:
                weather.append(each.text)
            #风向
            wind=[]
            target=soup.find_all('wind')
            for each in target:
                wind.append(each.text)
            #风力
            winp=[]
            target=soup.find_all('winp')
            for each in target:
                winp.append(each.text)

            for i in range(7):
                sql = "insert into weatherlist(weatherdate,weatherweek,cityname,temperature,weather,wind,winp) values('%s','%s','%s','%s','%s','%s','%s')"%(day[i],week[i],city[i],temperature[i],weather[i],wind[i],winp[i])
                sqlWrite(sql)

            data="" 
            flag = 0
            return render.weather(cityname,data,flag)
        
        if "history" in webData:
            sql = "select * from weatherlist"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.weather(cityname,sqlData,flag)
        
        if "delete" in webData:
            sql = "delete from weatherlist where cityname='%s'"%(cityname)
            sqlWrite(sql)
            sqlData = sqlSelect(sql)
            flag = 0
            return render.weather(cityname,sqlData,flag)


class workers:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            id = "1001"
            name = "请输入姓名"
            sex = "请输入性别"
            age = "请输入年龄"
            education = "请输入学历"
            address = "请输入住址"
            phone = "请输入电话"
            money = "请输入工资"
            data = ""
            flag = 1
            return render.workers(id,name,sex,age,education,address,phone,money,data,flag)

    def POST(self):
        
        webData = web.input()
        id = webData.get("id")
        name = webData.get("name")
        sex = webData.get("sex")
        age = webData.get("age")
        education = webData.get("education")
        address = webData.get("address")
        phone = webData.get("phone")
        money = webData.get("money")

        if "search" in webData:
            sql = "insert into workers(id,name,sex,age,education,address,phone,money) values('%s','%s','%s','%s','%s','%s','%s','%s')"%(id,name,sex,age,education,address,phone,money)
            sqlWrite(sql)
            sql = "select id,name,sex,age,education,address,phone,money from workers"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.workers(id,name,sex,age,education,address,phone,money,sqlData,flag)
        if "delete" in webData:
            sql = "delete from workers where id='%s'"%(id)
            sqlWrite(sql)
            sql = "select id,name,sex,age,education,address,phone,money from workers"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.workers(id,name,sex,age,education,address,phone,money,sqlData,flag)

        if "history" in webData:
            sql = "select id,name,sex,age,education,address,phone,money from workers"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.workers(id,name,sex,age,education,address,phone,money,sqlData,flag)


class books:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            id = "1001"
            bookname = "请输入书名"
            author = "请输入作者"
            reader = "请输入读者"
            bookdate = "请输入借阅日期"
            enddate = "请输入到期日期"
            phone = "请输入电话"
            money = "请输入押金"
            data = ""
            flag = 1
            return render.books(id,bookname,author,reader,bookdate,enddate,phone,money,data,flag)

    def POST(self):
        
        webData = web.input()
        id = webData.get("id")
        bookname = webData.get("bookname")
        author = webData.get("author")
        reader = webData.get("reader")
        bookdate = webData.get("bookdate")
        enddate = webData.get("enddate")
        phone = webData.get("phone")
        money = webData.get("money")

        if "search" in webData:
            sql = "insert into books(id,bookname,author,reader,bookdate,enddate,phone,money) values('%s','%s','%s','%s','%s','%s','%s','%s')"%(id,bookname,author,reader,bookdate,enddate,phone,money)
            sqlWrite(sql)
            sql = "select id,bookname,author,reader,bookdate,enddate,phone,money from books"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.books(id,bookname,author,reader,bookdate,enddate,phone,money,sqlData,flag)
        if "delete" in webData:
            sql = "delete from books where id='%s'"%(id)
            sqlWrite(sql)
            sql = "select id,bookname,author,reader,bookdate,enddate,phone,money from books"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.books(id,bookname,author,reader,bookdate,enddate,phone,money,sqlData,flag)

        if "history" in webData:
            sql = "select id,bookname,author,reader,bookdate,enddate,phone,money from books"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.books(id,bookname,author,reader,bookdate,enddate,phone,money,sqlData,flag)


class tongcheng:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            cityname = "5162"
            data=""
            flag = 1
            return render.tongcheng(cityname,data,flag)
        
    def POST(self):
        webData = web.input()
        cityname = webData.get("cityname")
        if "search" in webData:
            cityname="5162"
            j = 1
            for i in range(1,11):
                time.sleep(2)
                geturl = "https://www.ly.com/scenery/AjaxHelper/DianPingAjax.aspx?action=GetDianPingList&sid=%s&page="%cityname + str(i) + "&pageSize=10"
                request = requests.get(url=geturl, headers=headers)
                html = json.loads(request.text)
                print('正在爬取第' + str(i) + '页')
                # 解析数据
                datas = html['dpList']
                with open("tongcheng.txt", "a", newline='', encoding='utf-8') as f:
                    for k in datas:
                        f.write('(' + str(j) + ')' + k['dpContent'])
                        f.write("\n")
                        j += 1    
                for ii in datas:
                    sql = "insert into Contentlist (Content,cityname) values('%s','%s')"%(k['dpContent'],cityname)
                    sqlWrite(sql) 
            data="" 
            flag = 0
            return render.tongcheng(cityname,data,flag)
        
        if "history" in webData:
            sql = "select * from Contentlist"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.tongcheng(cityname,sqlData,flag)
        
        if "delete" in webData:
            sql = "delete from Contentlist where cityname='%s'"%(cityname)
            sqlWrite(sql)
            sqlData = sqlSelect(sql)
            flag = 0
            return render.tongcheng(cityname,sqlData,flag)
        


class students:
    def GET(self):
        print(session.get('name'))
        if session.get('name')==None:
            raise web.seeother('/login.html')
        else:
            id = "1001"
            name = "请输入姓名"
            sex = "请输入性别"
            age = "请输入年龄"
            education = "请输入学历"
            address = "请输入住址"
            phone = "请输入电话"
            money = "请输入工资"
            data = ""
            flag = 1
            return render.workers(id,name,sex,age,education,address,phone,money,data,flag)

    def POST(self):
        
        webData = web.input()
        id = webData.get("id")
        name = webData.get("name")
        sex = webData.get("sex")
        age = webData.get("age")
        education = webData.get("education")
        address = webData.get("address")
        phone = webData.get("phone")
        money = webData.get("money")

        if "search" in webData:
            sql = "insert into workers(id,name,sex,age,education,address,phone,money) values('%s','%s','%s','%s','%s','%s','%s','%s')"%(id,name,sex,age,education,address,phone,money)
            sqlWrite(sql)
            sql = "select id,name,sex,age,education,address,phone,money from workers"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.workers(id,name,sex,age,education,address,phone,money,sqlData,flag)
        if "delete" in webData:
            sql = "delete from workers where id='%s'"%(id)
            sqlWrite(sql)
            sql = "select id,name,sex,age,education,address,phone,money from workers"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.workers(id,name,sex,age,education,address,phone,money,sqlData,flag)

        if "history" in webData:
            sql = "select id,name,sex,age,education,address,phone,money from workers"
            sqlData = sqlSelect(sql)
            flag = 0
            return render.workers(id,name,sex,age,education,address,phone,money,sqlData,flag)



render = web.template.render(r'C:\VS Code\Python\Python_Web\python_web_bootstrap_project\templates')
web.config.debug = False
app = web.application(urls, globals())
import tempfile

root = tempfile.mkdtemp()
store = web.session.DiskStore(root)
session = web.session.Session(app, store)


if __name__ == "__main__":
    app.run()


