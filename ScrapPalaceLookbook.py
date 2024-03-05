#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Im więcej rzeczy przerzucisz do funkcji tym szybciej się wykona.. ;/

import urllib.request as urllib2
import requests
import re
import sys
#import time
import os
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
from datetime import datetime
from pathlib import PurePosixPath

DEBUG = False

def log(s):
    if DEBUG:
        print(s)

class Souper(BeautifulSoup):
    "Class Souper"

    pages = {
                "PS_UK"   : "https://shop.palaceskateboards.com",
                "PS_US"   : "https://shop-usa.palaceskateboards.com",
                "SUP"     : "https://www.supremenewyork.com",
                "ETC_PS"  : "/collections/new" if date.today().month != 2 else "",
                "ETC_SUP" : "/shop/all" if BeautifulSoup(requests.get("https://www.supremenewyork.com/shop/new").content,'html.parser').find("div",id="wrap").find("div",id="container").text == '' else "/shop/new"
            }


    data =  {
                "name"       : [],
                "name_us"    : [],
                "name_sup"   : [],
                "price_gbp"  : [],
                "price_us"   : [],
                "price_sup"  : [],
                "desc"       : [],
                "desc_us"    : [],
                "desc_sup"   : [],
                "model_sup"  : [],
                "color_sup"  : dict(),
                "category"   : []
             }
    VPN = {
            "UK"  : False,
            "JPN" : False
          }
    pathPalace='palaceskateboards'
    pathSupreme='supreme' 
    
    count = 1
    def worker_fillDirectory_UK(self):

        for x in self.findAll('div',class_='product-grid-item clearfix'):
                if re.search('href=\"(\/+\w+\/+\w+[^\"])\"',str(x)) == None:
                        continue
                doup = Souper(requests.get(self.pages['PS_UK']+(re.search('href=\"(\/+\w+\/+\w+[^\"])\"',str(x))).group(1)).content,'html.parser')
                self.data['name'].append((re.search('<h1 class=\"+\w+\"\>(.*?)<\/h1>',str(doup)).group(1)))
                self.data['desc'].append(doup.find('ul').text)
                self.data['price_gbp'].append('' if re.search('<span class=\"prod\-price\" .*?\>.(\d{0,})<\/span>',str(doup)) == None else re.search('<span class=\"prod\-price\" .*?\>.(\d{0,})<\/span>',str(doup)).group(1))
                
                if not os.path.exists(self.pathPalace +'/'+self.data['name'][-1].replace('/','_')):
                        os.makedirs(self.pathPalace +'/'+self.data['name'][-1].replace('/','_'))
                count = 0
                for z in doup.findAll('img'):
                        if z.get('data-zoom') != None:
                            with open(self.pathPalace + '/'+self.data['name'][-1].replace('/','_')+'/'+os.path.basename(self.data['name'][-1].replace('/','_'))+str(count)+'.jpg', 'wb') as fd:
                                for chunk in requests.get('https:'+z.get('data-zoom')).iter_content(chunk_size=128):
                                    fd.write(chunk)
                                count+=1
                                
    def worker_fillDirectory_US(self):
        for x in self.findAll('div',class_='product-grid-item clearfix'):
                if re.search('href=\"(\/+\w+\/+\w+[^\"])\"',str(x)) == None:
                        continue
                doup = Souper(requests.get(self.pages['PS_US']+(re.search('href=\"(\/+\w+\/+\w+[^\"])\"',str(x))).group(1)).content,'html.parser')
                self.data['name_us'].append((re.search('<h1 class=\"+\w+\"\>(.*?)<\/h1>',str(doup)).group(1)))
                self.data['desc_us'].append(doup.find('ul').text)
                self.data['price_us'].append('' if re.search('<span class=\"prod\-price\" .*?\>.(\d{0,})<\/span>',str(doup)) == None else re.search('<span class=\"prod\-price\" .*?\>.(\d{0,})<\/span>',str(doup)).group(1))
                if not os.path.exists(self.pathPalace +'/'+self.data['name_us'][-1].replace('/','_')):
                    os.makedirs(self.pathPalace +'/'+self.data['name_us'][-1].replace('/','_'))
                count = 0
                for z in doup.findAll('img'):
                    if z.get('data-zoom') != None:
                        with open(self.pathPalace + '/'+self.data['name_us'][-1].replace('/','_')+'/'+os.path.basename(self.data['name_us'][-1].replace('/','_'))+str(count)+'.jpg', 'wb') as fd:
                            for chunk in requests.get('https:'+z.get('data-zoom')).iter_content(chunk_size=128):
                                fd.write(chunk)
                        count+=1

    def fillDirectoryPS(self,typeRequest):
              
        if typeRequest in "PS_UK": # UK
            self.worker_fillDirectory_UK()
            tmp_a = self.find('a',id='pager-next-url')
            
            while tmp_a != None:
                if tmp_a is None:
                    continue
                
                self.__dict__ = Souper(requests.get(self.pages["PS_UK"]+tmp_a.get('href')).content,'html.parser').__dict__
                self.worker_fillDirectory_UK()
                tmp_a = self.find('a',id='pager-next-url')
                
        elif typeRequest in "PS_US": # US
            self.worker_fillDirectory_US()
            tmp_a = self.find('a',id='pager-next-url')
            
            while tmp_a != None:
                if tmp_a is None:
                    continue
                
                self.__dict__ = Souper(requests.get(self.pages["PS_US"]+tmp_a.get('href')).content,'html.parser').__dict__
                self.worker_fillDirectory_US()
                tmp_a = self.find('a',id='pager-next-url')
                    

            
    def fillDirectorySup(self):        
        for x in self.findAll('div',class_='inner-article'):
            doup = Souper(requests.get(self.pages["SUP"]+x.a.get('href')).content,'html.parser')
            self.data["name_sup"].append(doup.find('h1',itemprop = 'name').text)
            self.data["category"].append(doup.find('h1',itemprop = 'name')['data-category'])
            self.data['model_sup'].append(doup.find('p',itemprop = 'model').text)
            
            if self.data["name_sup"][-1] in self.data['color_sup'].keys():
                self.data['color_sup'][self.data["name_sup"][-1]] += ", "+self.data['model_sup'][-1]
            else:
                self.data['color_sup'][self.data["name_sup"][-1]] = self.data['model_sup'][-1]
            
            self.data["desc_sup"].append(doup.find('p',class_= 'description').text)
            self.data["price_sup"].append('' if doup.find('span', itemprop = 'price') == None else doup.find('span',itemprop = 'price').text)
            
            if not os.path.exists(self.pathSupreme+'/'+self.data["name_sup"][-1].replace('/','_')):
                os.makedirs(self.pathSupreme+'/'+self.data["name_sup"][-1].replace('/','_'))
            count = 0
            for z in doup.findAll('button',{'data-style-name': doup.find('p',itemprop = 'model').text}):
                if z.get('data-url') != None:
                    with open(os.path.realpath(self.pathSupreme+'/'+self.data["name_sup"][-1].replace('/','_'))+'/'+os.path.basename(self.data["name_sup"][-1])+' '+self.data["model_sup"][-1]+str(count)+'.jpg', 'wb') as fd:
                        for chunk in requests.get('https:'+(re.search('\"zoomed_url\":\"(\/\/+\w+.+[^\}\"])',z.get('data-images'))).group(1)).iter_content(chunk_size=128):
                            fd.write(chunk)
                    count+=1
                   
    def fillDirectorySupVPN(self):
        if 'en-gb' in self.body['class']: # vpn == uk
            for x in self.findAll('div',class_='inner-article'):
                    doup = Souper(requests.get(self.pages["SUP"]+x.a.get('href')).content,'html.parser')
                    self.data["name_sup"].append(doup.find('h1',itemprop = 'name').text)
                    self.data["category"].append(doup.find('h1',itemprop = 'name')['data-category'])
                    self.data['model_sup'].append(doup.find('p',itemprop = 'model').text)
                    #print(doup.find('span', itemprop = 'price').text)
                    if self.data["name_sup"][-1] in self.data['color_sup'].keys():
                        self.data['color_sup'][self.data["name_sup"][-1]] += ", "+self.data['model_sup'][-1]
                    else:
                        self.data['color_sup'][self.data["name_sup"][-1]] = self.data['model_sup'][-1]
                    self.data["desc_sup"].append(doup.find('p',class_= 'description').text)
                    self.data["price_sup"].append('' if doup.find('span', itemprop = 'price') == None else doup.find('span',itemprop = 'price').text)


        else: # vpn == jpn
            for x in self.findAll('div',class_='inner-article'):
                print(self.pages["SUP"]+x.a.get('href'))
                doup = Souper(requests.get(self.pages["SUP"]+x.a.get('href')).content,'html.parser')
                self.data["name_sup"].append(doup.find('h1',itemprop = 'name').text)
                self.data["category"].append(doup.find('h1',itemprop = 'name')['data-category'])
                self.data['model_sup'].append(doup.find('p',itemprop = 'model').text)

                if self.data["name_sup"][-1] in self.data['color_sup'].keys():
                    self.data['color_sup'][self.data["name_sup"][-1]] += ", "+self.data['model_sup'][-1]
                else:
                    self.data['color_sup'][self.data["name_sup"][-1]] = self.data['model_sup'][-1]                       
                            
                self.data["desc_sup"].append(doup.find('p',class_= 'description').text)
                self.data["price_sup"].append('' if re.search('<span.*?\>.(\d{0,}).(\d{0,})<\/span>',str(doup)) == None else str(re.search('<span.*?\>.(\d{0,}).(\d{0,})<\/span>',str(doup)).group(1)+re.search('<span.*?\>.(\d{0,}).(\d{0,})<\/span>',str(doup)).group(2))) # vpn jpn

    def callFillDirectory(self):
        if datetime.now().strftime("%H:%M") < '17:00': # before at 17:00 hour - drop UK
            
            self.fillDirectoryPS("PS_UK")
            
        else: # after at 17:00 hour - drop USA
            
            self.fillDirectoryPS("PS_US")
    
    def callFillDirectorySup(self,VPN):
        if VPN in ['n','N']:
            self.fillDirectorySup()
        else:
            self.fillDirectorySupVPN() #Supreme Foreign

# ___________________________________Insert to CalcSheet________________________________
        
    def insertToCalcSheet(self,path):

        if datetime.now().strftime("%H:%M") < '17:00': # before at 17:00 hour - drop UK
            # PALACESKATEBOARD UK BEGIN
            
            self.data["desc"] = [str(x).replace(u'\xa0',u' ') for x in self.data["desc"]]
            self.data["desc"] = [str(x).replace(u'\n',u' ') for x in self.data["desc"]]
            self.data["desc"] = [' '.join(x.split()) for x in self.data["desc"]]
            self.data["desc"] = [x.upper() for x in self.data["desc"]]
            
            # PALACESKATEBOARD UK END

            # PREPARE DATA TO INSERT CALCSHEET
            
            s1 = pd.Series(self.data["name_us"] if len(self.data["name_us"]) > len(self.data["name"]) else self.data["name"], name='nazwa')
            s4 = pd.Series(self.data["desc"] if len(self.data["desc"]) > len(self.data["desc_us"]) else self.data["desc"], name='opis')
            s2 = pd.Series(self.data["price_us"], name='cena $')
            s3 = pd.Series(self.data["price_gbp"], name='cena £')
            st = pd.Series([(date.today()).isoformat() for x in range(len(s1))], name='data')

            # CONCAT COLUMNS PREPARED DATA
            
            dfs = pd.concat([s1,s2,s3,s4,st], axis=1)

            # INSERT CONCATED COLUMNS TO EXCEL [ PALACESKATEBOARD UK ]
            dfs.to_excel(path+'/'+"output.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
            df_tmp = pd.read_excel(path+'/'+"output.xlsx")
            df_tmp.to_excel(path+'/'+"output.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8') # delete ' from number
            
        else:
            # PALACESKATEBOARD USA BEGIN
            if not os.path.exists(path+'/'+"output.xlsx"):
                s1 = pd.Series(self.data["name_us"], name='nazwa')
                s4 = pd.Series(self.data["desc_us"], name='opis')
                s2 = pd.Series(self.data["price_us"], name='cena $')
                s3 = pd.Series('', name='cena £')
                st = pd.Series([(date.today()).isoformat() for x in range(len(s1))], name='data')
                
                self.data["desc_us"] = [str(x).replace(u'\xa0',u' ') for x in self.data["desc_us"]]
                self.data["desc_us"] = [str(x).replace(u'\n',u' ') for x in self.data["desc_us"]]
                self.data["desc_us"] = [' '.join(x.split()) for x in self.data["desc_us"]]
                # CONCAT COLUMNS PREPARED DATA
                
                dfs = pd.concat([s1,s2,s3,s4,st], axis=1)

                # INSERT CONCATED COLUMNS TO EXCEL [ PALACESKATEBOARD UK ]
                dfs.to_excel(path+'/'+"output.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
                df_tmp = pd.read_excel(path+'/'+"output.xlsx")
                df_tmp.to_excel(path+'/'+"output.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
            else:
                dfs = pd.read_excel(path+'/'+"output.xlsx")
                #print("SELF PRICE_US:\n",self.data["price_us"])
                dfs['cena $'] = pd.Series(self.data["price_us"], name='cena $')
                #print(dfs['cena $'],pd.Series(self.data["price_us"], name='cena $'))
                self.data["desc_us"] = [str(x).replace(u'\xa0',u' ') for x in self.data["desc_us"]]
                self.data["desc_us"] = [str(x).replace(u'\n',u' ') for x in self.data["desc_us"]]
                self.data["desc_us"] = [' '.join(x.split()) for x in self.data["desc_us"]]
                #print([x for x in zip_longest(data["name"],data["name_us"],data["price_gbp"],data["price_us"])])
                
                # INSERT CONCATED COLUMNS TO EXCEL [ PALACESKATEBOARD UK & USA ]
                dfs.to_excel(path+'/'+"output.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
                df_tmp = pd.read_excel(path+'/'+"output.xlsx")
                df_tmp.to_excel(path+'/'+"output.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
                
                # PALACESKATEBOARD USA END

    def insertToCalcSheetSup(self,VPN):
        if VPN in ['n','N']:
            # SUPREME BEGIN

            color,name,price,desc,category = [],[],[],[],[]

            self.data["price_sup"] = [str(x).replace(u'€',u'') for x in self.data["price_sup"]]
            for x in range(len(self.data["name_sup"])):
                if self.data["name_sup"][x] != self.data["name_sup"][x-1]:
                    color.append(self.data['color_sup'][self.data["name_sup"][x]])
                    name.append(self.data["name_sup"][x])
                    price.append(self.data["price_sup"][x])
                    category.append(self.data["category"][x])
                    desc.append(self.data["desc_sup"][x])

            # SUPREME END

            print(len(self.data["name_sup"]),len(color))

            # ORDER DATA FROM SUPREME
            df = pd.DataFrame({
                                    'kategoria'   : category,
                                    'nazwa'       : name,
                                    'kolorystyka' : color,
                                    'cena €'      : price,
                                    'opis'        : desc,
                                    'data'        : (date.today()).isoformat()
                               },columns=['kategoria','nazwa','kolorystyka','cena €','opis','data'])

            #DROP DUPLICATES FROM SUPREME
            df.drop_duplicates(inplace=True)

            # INSERT ORDERED DATA TO EXCEL [ SUPREME ]
            df.to_excel(self.pathSupreme+'/'+"output2.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
            df_tmp = pd.read_excel(self.pathSupreme+'/'+"output2.xlsx")
            df_tmp.to_excel(self.pathSupreme+'/'+"output2.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
        else:
            if 'en-gb' in self.body['class']: # vpn == uk
                color,name,price,desc,category = [],[],[],[],[]

                self.data["price_sup"] = [str(x).replace(u'£',u'') for x in self.data["price_sup"]]
                for x in range(len(self.data["name_sup"])):
                        if self.data["name_sup"][x] != self.data["name_sup"][x-1]:
                            color.append(self.data['color_sup'][self.data["name_sup"][x]])
                            name.append(self.data["name_sup"][x])
                            price.append(self.data["price_sup"][x])
                            desc.append(self.data["desc_sup"][x])
                            category.append(self.data["category"][x])
                df = pd.DataFrame({
                                       'kategoria'   : category,
                                       'nazwa'       : name,
                                       'kolorystyka' : color,
                                       'cena £'      : price,
                                       'opis'        : desc,
                                       'data'        : (date.today()).isoformat()
                                   },columns=['kategoria','nazwa','kolorystyka','cena £','opis','data'])

                df.drop_duplicates(inplace=True)
                df.to_excel(self.pathSupreme+'/'+"output2.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
                df_tmp = pd.read_excel(self.pathSupreme+'/'+"output2.xlsx")
                df_tmp.to_excel(self.pathSupreme+'/'+"output2.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
            else: # vpn == jpn
                color,name,price,desc,category = [],[],[],[],[]
                
                for x in range(len(self.data["name_sup"])):
                    if self.data["name_sup"][x] != self.data["name_sup"][x-1]:
                        color.append(self.data['color_sup'][self.data["name_sup"][x]])
                        name.append(self.data["name_sup"][x])
                        price.append(self.data["price_sup"][x])
                        desc.append(self.data["desc_sup"][x])
                        category.append(self.data["category"][x])
                        
                df = pd.DataFrame({
                                        'kategoria'   : category,
                                        'nazwa'       : name,
                                        'kolorystyka' : color,
                                        'cena ¥'      : price,
                                        'opis'        : desc,
                                        'data'        : (date.today()).isoformat()
                                   },columns=['kategoria','nazwa','kolorystyka','cena ¥','opis','data'])
                
                df.drop_duplicates(inplace=True)
                df.to_excel(self.pathSupreme+'/'+"output2.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
                df_tmp = pd.read_excel(self.pathSupreme+'/'+"output2.xlsx")
                df_tmp.to_excel(self.pathSupreme+'/'+"output2.xlsx",sheet_name='Sheet_name_1',index=False,encoding='utf-8')
                
    def scrapLookBooks(self,URL):
        #print(self.find('a',{"href":"/lookbook/"+str(URL) if isinstance(URL,int) else "/lookbook/"+os.path.basename(URL)}))
        d = str(self.find('button',{"data-url":"/lookbook/"+str(URL) if isinstance(URL,int) else "/lookbook/"+os.path.basename(URL)}).text).replace("/","_") if "lookbooks" not in str(URL) else " ".join(str(self.title.text).split(' ')[:3]).replace("/","_")
        pathLookBook = self.pathSupreme+"/"+"LookBook"+"/"+d
        if not os.path.exists(pathLookBook):
            os.makedirs(pathLookBook)
        with open(pathLookBook+'/'+d+'.txt', 'w') as f:
            f.write("")
        for x in self.findAll('button'):
            with open(pathLookBook+'/'+d+'.txt', 'a') as f:
                f.write("%s\n" % PurePosixPath(x["data-zoomed-image-url"]).name)
                f.write('\n'.join(re.findall('<a href=\'.*?\'>(.*?)</a>',str(x["data-caption"]))))
                f.write("\n\n")
            
            with open(pathLookBook +"/"+PurePosixPath(x["data-zoomed-image-url"]).name, 'wb') as fd: # download pictures
                for chunk in requests.get('https:'+x["data-zoomed-image-url"]).iter_content(chunk_size=128):
                    fd.write(chunk)
                    
def createDirectories(Palace,Supreme):
    if not os.path.exists(Palace):
        os.makedirs(Palace)
    if not os.path.exists(Supreme):
        os.makedirs(pathSupreme)
            
pathPalace='palaceskateboards'
pathSupreme='supreme' 

pages = {
            "PS_UK"    : "https://shop.palaceskateboards.com",
            "PS_US"    : "https://shop-usa.palaceskateboards.com",
            "SUP"      : "https://www.supremenewyork.com",
            "ETC_PS"   : "/collections/new" if date.today().month != 2 else "",
            "ETC_SUP"  : "/shop/all" if BeautifulSoup(requests.get("https://www.supremenewyork.com/shop/new").content,'html.parser').find("div",id="wrap").find("div",id="container").text == '' else "/shop/new",
            "Look_SUP" : "/lookbook"
        }


chosenVPN = input("VPN(Y/N)")
createDirectories(pathPalace,pathSupreme)

if chosenVPN in ['N','n']:

    if datetime.now().strftime("%H:%M") < '17:00':
        soup = Souper(requests.get(pages["PS_UK"]+pages["ETC_PS"]).content, 'html.parser') # uk
        soup.callFillDirectory()
        print("EXCELL")
        soup.insertToCalcSheet(pathPalace)
    else:
        soup_us = Souper(requests.get(pages["PS_US"]+pages["ETC_PS"]).content,'html.parser') # usa
        soup_us.callFillDirectory()
        print("EXCELL")
        soup_us.insertToCalcSheet(pathPalace)
    print("SUPREME")
    soup_sup = Souper(requests.get(pages["SUP"]+pages["ETC_SUP"]).content, 'html.parser') # supreme
    soup_sup.callFillDirectorySup(chosenVPN)
    soup_sup.insertToCalcSheetSup(chosenVPN)

    url = str(input("Podaj Url: ")) if input("Czy chcesz podać pełny URL?(T/N) ") in ['t','T'] else int(input("Podaj nr: "))
    soup_sup_book = Souper(requests.get(pages["SUP"]+pages["Look_SUP"]+'/'+str(url) if isinstance(url,int) else url).content, 'html.parser') # supreme
    soup_sup_book.scrapLookBooks(url)
    
    
else: #VPN ON,baby :P
    soup_sup = Souper(requests.get(pages["SUP"]+pages["ETC_SUP"]).content, 'html.parser') # supreme
    soup_sup.callFillDirectorySup(chosenVPN)
    soup_sup.insertToCalcSheetSup(chosenVPN)
