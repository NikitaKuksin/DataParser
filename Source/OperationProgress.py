
import sys
path_source_cod = r'/content/drive/MyDrive/Магистратура/Научная_работа/Parser/Source/'
sys.path.append(path_source_cod)

from constants import path_OperationProgress, path_HTML_history
from get_name import get_name_history
from get_cod import get_cod_history

import re
from os import walk, listdir
from bs4 import BeautifulSoup
from tqdm import tqdm
import datetime
import pandas as pd
import numpy as np

#------------------------------------------------------------------------------------Выгрузка документов вида "Ход операции"

def get_OperationProgress_docs():
    table = []
    print( "Загрузка документов вида \"Ход операции\" начата" )
    for file in tqdm(listdir(path_HTML_history)):
        if '.html' not in file:
                continue
        with open(f'{path_HTML_history}/{file}', encoding='utf-8') as file:
                        src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        name = None
        cod = None
        find = "Нет"

        name = get_name_history(soup)
        cod = get_cod_history(soup)

        htmls = get_OperationProgress_doc(src)
        if( len(htmls) > 0 and htmls[0] != None ):
          find = "Да"
          for html in htmls :
            table.append(
                {
                    "File Name": file.name,
                    "Name": str(name),
                    "Cod": str(cod),
                    "Find": find,
                    "HTML": html,
                }
          )
        else:
          table.append(
                {
                    "File Name": file.name,
                    "Name": str(name),
                    "Cod": str(cod),
                    "Find": find,
                    "HTML": None,
                }
            
        )

    table_df = pd.DataFrame( table )
    table_df.to_excel(path_OperationProgress,engine='xlsxwriter')
    print( "Загрузка документов вида \"Ход операции\" окончена, данные выгружены в таблицу : \n\t\t"+path_OperationProgress )
    return table_df

def get_OperationProgress_doc(text):
    text_reserv = text
    res = [  ]
    doc = "<h4>Ход операции</h4>"

    while ( text.find(doc) != -1  ):
      index_beging = text.find(doc)
      if( index_beging == -1 ):
        return None
      
      text = text[index_beging:]

      iter_line = re.finditer("<hr>",text)
      index_line = []
      for i in iter_line:
        index_line.append( i.start() )

      if( len(index_line)>=0 ):
        res.append( text[:index_line[2]] )
        text = text[index_line[2]:]
      else:
        res.append( None )
        text = text[index_line[0]:]

    return res

def get_OperationProgress_value( hodOper ):
    
    print( "Разбор документов вида \"Ход операции\" начат" )

    hodOper["Начало операции"] = None
    hodOper["Конец операции"] = None
    hodOper["Вид операции"] = None
    hodOper["Экстренная"] = None

    for index in tqdm(hodOper.index):
        html = hodOper["HTML"][index]
        if( type(html) == float or html != None ):
            continue

        html = html.replace("&nbsp;"," ")
        end  = None
        beging = None
        emergency = None
        type_operation = None
        #---------------------------------------------------------------------------Начало операции
        try:
            if( re.search( "<br>[ ]*Дата: \d+\.\d+\.\d+", html) ):
                beging_date = re.findall( "<br>[ ]*Дата: \d+\.\d+\.\d+", html)
                beging_date = re.findall( "\d+\.\d+\.\d+", beging_date[0])[0]
            elif( re.search( "</center>[ ]*Дата: \d+\.\d+\.\d+", html) ):
                beging_date = re.findall( "</center>[ ]*Дата: \d+\.\d+\.\d+", html)
                beging_date = re.findall( "\d+\.\d+\.\d+", beging_date[0])[0]
            else:
                beging_date = None
        except Exception as e:
            print(e)
            beging_date = None
              
        try:    
            beging_time = re.findall( " начало: \d+[\. :]+\d+", html)
            if( len(beging_time) > 0 ):
                beging_time = re.findall( "\d+[\. :]+\d+", beging_time[0])[0]
                beging_time = beging_time.replace( ":", "." )
                beging_time = beging_time.replace( " ", "." )
            else:
                beging_time = None
        except Exception as e:
            print(e)
            beging_date = None
        
        try:
            if( beging_date != None and beging_time != None ):
                beging = datetime.datetime.strptime( beging_date + " " + beging_time, '%d.%m.%Y %H.%M' )
        except Exception as e:
            print(e)
            beging = None
        
        #---------------------------------------------------------------------------Конец операции
        try:
            if( re.search( "  конец: \d+\.\d+\.\d+ \d+[\. :]+\d+", html) ):
                end_date = re.findall( "  конец: \d+\.\d+\.\d+ \d+[\. :]+\d+", html)
                end_date = re.findall( "\d+\.\d+\.\d+", end_date[0])[0]
            elif( beging_date != None ):
                end_date = beging_date
            else:
                beging_date = None
        except Exception as e:
            print(e)
            beging_date = None   
        
        try:
            if( re.search( "  конец: \d+\.\d+\.\d+ \d+[\. :]+\d+", html) ):
                end_time = re.findall( "  конец: \d+\.\d+\.\d+ \d+[\. :]+\d+", html)
                end_time = re.findall( "\d \d+[\. :]+\d+", end_time[0])[0]
                end_time = end_time[2:]
                end_time = end_time.replace( ":", "." )
                end_time = end_time.replace( " ", "." )
            elif( re.search( "  конец: \d+[\. :]+\d+", html) ):
                end_time = re.findall( "  конец: \d+[\. :]+\d+", html)
                end_time = re.findall( "\d+[\. :]+\d+", end_time[0])[0]
                end_time = end_time.replace( ":", "." )
                end_time = end_time.replace( " ", "." )
            else:
                end_time = None
        except Exception as e:
            print(e)
            end_time = None  
    
        try:
            if( beging_date != None and beging_time != None ):
                beging = datetime.datetime.strptime( beging_date + " " + beging_time, '%d.%m.%Y %H.%M' )
            if( end_date != None and end_time != None ):
                try:
                  end = datetime.datetime.strptime( end_date + " " + end_time, '%d.%m.%Y %H.%M' )
                except Exception as e:
                  end = e
        except Exception as e:
            print(e)
            end_time = None 

        #---------------------------------------------------------------------------Вид операции        
        soup = BeautifulSoup(html, 'lxml')
        if(       soup.find('span',string = re.compile( "ТЛБАП|талбап" )) != None
              or  ( soup.find('span') != None
                    and re.search("ТЛБАП|талбап",soup.find('span').text) )
              or    soup.find('p',string = re.compile( "ТЛБАП|талбап" )) != None
              or  ( soup.find('p') != None
                    and re.search("ТЛБАП|талбап",soup.find('p').text) ) 
              or  soup.find('font',string = re.compile( "ТЛБАП|талбап" )) != None
              or  soup.find('b',string = re.compile( "ТЛБАП|талбап" )) != None
              or  ( soup.find('b') != None
                    and re.search("ТЛБАП|талбап",soup.find('b').text) ) 
              or  ( soup.find('font') != None
                    and re.search("ТЛБАП|талбап",soup.find('font').text) ) ):
            type_operation = "ТЛБАП"
        elif(     soup.find('span',string = re.compile( "реканализац" )) != None
              or  soup.find('font',string = re.compile( "реканализац" )) != None
            or  soup.find('b',string = re.compile( "реканализац" )) != None):
            type_operation = "Реканализация"
        elif( re.search( "<b>реваскуляризация миокарда</b>", html) ):
            type_operation = "Реваскуляризация миокарда"
        elif( re.search( "<b>Аорто-коронарное шунтирование", html) ):
            type_operation = "Аорто-коронарное шунтирование"
        elif( re.search( "<b>Аорто-бифеморальное шунтирование", html) ):
            type_operation = "Аорто-бифеморальное шунтирование"
        elif( re.search( "<b>Протезирование", html) ):
            type_operation = "Протезирование"
        else:
            type_operation = None

        #---------------------------------------------------------------------------Экстренная
        if( re.search( "<b>плановая</b>", html) ):
            emergency = "Плановая"
        elif( re.search( "<b>экстренная</b>", html) ):
            emergency = "Экстренная"
        else:
            emergency = None

        hodOper["Начало операции"][index] = beging
        hodOper["Конец операции"][index] = end
        hodOper["Вид операции"][index] = type_operation
        hodOper["Экстренная"][index] = emergency
        
    hodOper.to_excel(path_OperationProgress,engine='xlsxwriter')
    print( "Разбор документов вида \"Ход операции\" окончен, данные сохранены в таблицу: \n\t\t"+path_OperationProgress )


def get_OperationProgress(  ):
    OperationProgress_df = get_OperationProgress_docs()
    get_OperationProgress_value( OperationProgress_df )

