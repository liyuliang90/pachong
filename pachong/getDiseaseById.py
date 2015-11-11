# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import urllib
import urllib.request
from urllib.error import URLError, HTTPError
import json
import mysql
import mysql.connector
import configparser
import time

class GetChunYu(object):
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read('pachong.conf')
        mysql_ip = cf.get('mysql','db_ip')
        mysql_port = cf.get('mysql','db_port')
        mysql_user = cf.get('mysql','db_user')
        mysql_passwd = cf.get('mysql','db_passwd')
        db_name = cf.get('mysql','db_name')
        self.conn=mysql.connector.connect(host=mysql_ip,user=mysql_user,passwd=mysql_passwd,db=db_name,charset="utf8")
        self.cursor = self.conn.cursor()
        self.insert_sql = "insert into diseases_detail values (%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"

    def getone(self,diseaseId,url):
        result_json=self.qingqiu_timeout(url)
        if not result_json:
            return
        buffer_json=result_json.read().decode()
        result_dict=json.loads(buffer_json)
        self.insert_one(diseaseId,result_dict)

    def replace_str(self,s_str):
        s_rep = '\r\n'
        s_rep2 = '\n'
        t_rep = '<br\>'
        if not s_str:
            return ''
        return s_str.replace(s_rep,t_rep).replace(s_rep2,t_rep)

    def insert_one(self,diseaseId,result_dict):
        id = result_dict.get('id',0)
        name = result_dict.get('name','')
        alias = result_dict.get('alias',[])
        alias = self.replace_str(','.join(alias))
        attention = self.replace_str(result_dict.get('attention',''))
        cause = self.replace_str(result_dict.get('cause',''))
        checkups = self.replace_str(result_dict.get('checkups',''))
        con_symptoms = self.replace_str(result_dict.get('con_symptoms',''))
        cure = self.replace_str(result_dict.get('cure',''))
        department =  result_dict.get('department',[])
        department = self.replace_str(','.join(department))
        description = self.replace_str(result_dict.get('description',''))
        diagnosis = self.replace_str(result_dict.get('diagnosis',''))
        prevention = self.replace_str(result_dict.get('prevention',''))
        symptoms = self.replace_str(result_dict.get('symptoms',''))
        sql_insert = self.insert_sql%(id,name,alias,attention,cause,checkups,con_symptoms,cure,
                                      department,description,diagnosis,prevention,symptoms)
        try:
            self.cursor.execute(sql_insert)
            self.conn.commit()
        except Exception:
            print (" insert to detail error %s"%diseaseId)
            self.saveDiseasesId(diseaseId)
            self.conn.rollback()

    def saveDiseasesId(self,diseaseId):
        insert_sql = "insert into out_diseases_id (disease_id) VALUES (%s);"
        sql_exe = insert_sql%diseaseId
        try:
            self.cursor.execute(sql_exe)
            self.conn.commit()
        except Exception:
            print ('insert to out error %s'%diseaseId)
            self.conn.rollback()

    def qingqiu_timeout(self,url):
            attempts = 0
            result = ""
            while attempts < 20:
                try:
                    result= urllib.request.urlopen(url,timeout=3)
                    return result
                except HTTPError as e:
                    print('HTTPError code: ', e.code)
                    attempts+=1
                except URLError as e:
                    print('URLReason: ', e.reason)
                    attempts+=1
                except Exception:
                    return result
            return result

def main():
    url = "https://api.chunyuyisheng.com/api/v4/disease_detail/%s" \
          "/?platform=iPhone&systemVer=8.4&version=6.3.0&app_ver=6.3.0&vendor=ziyou&phoneType=iPad&device_id=18908f6df4df40579a1d4b0616830beb&push_id=&app=0&"
    count = 30000
    chunyu = GetChunYu()
    for i in range(count):
        print (i)
        myurl = url%i
        chunyu.getone(i,myurl)
        time.sleep(2)

if __name__ =='__main__':
    main()
