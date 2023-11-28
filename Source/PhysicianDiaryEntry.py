
import sys
path_source_cod = r'/content/drive/MyDrive/Магистратура/Научная_работа/Parser/Source/'
sys.path.append(path_source_cod)

from constants import path_PhysicianDiaryEntry, path_HTML_history
from get_name import get_name_history
from get_cod import get_cod_history

import re
from os import walk, listdir
from bs4 import BeautifulSoup
from tqdm import tqdm
import datetime
import pandas as pd
import numpy as np

#------------------------------------------------------------------------------------Выгрузка документов вида "Дневниковая запись лечащего врача"

def get_PhysicianDiaryEntry_docs():
    print( "Загрузка документов вида \"Дневниковая запись лечащего врача\" начата" )
    table = []
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

        htmls = get_PhysicianDiaryEntry_doc(src)

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
                })
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
    table_df.to_excel(path_PhysicianDiaryEntry,engine='xlsxwriter')
    print( "Загрузка документов вида \"Дневниковая запись лечащего врача\" окончена, данные выгружены в таблицу : \n\t\t"+path_PhysicianDiaryEntry )

def get_PhysicianDiaryEntry_doc(text):

    res = [  ]
    doc = "<center><b>Дневниковая запись лечащего врача</b></center>"
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
        res.append( text[:index_line[0]] )
        text = text[index_line[0]:]
      else:
        res.append( None )
    
    return res

def get_PhysicianDiaryEntry_value( devZapLechVrach ):

      print( "Разбор документов вида \"Дневниковая запись лечащего врача\" начат" )

      devZapLechVrach["Дата"] = None
      devZapLechVrach["САД"] = None
      devZapLechVrach["ДАД"] = None
      devZapLechVrach["ЧСС"] = None
      devZapLechVrach["Пульс"] = None
      devZapLechVrach["ЧДД"] = None
      devZapLechVrach["Оценка болевого синдрома по ВАШ"] = None
      devZapLechVrach["Температура"] = None

      for index in tqdm(devZapLechVrach.index):
          html = devZapLechVrach["HTML"][index]
          html = html.replace("&nbsp;"," ")

          soup = BeautifulSoup(html, 'lxml')
          name = soup.find('p')
          if( name == None ):
            continue
          inform = name.find_next('p')

          time = None
          sad = None
          dad = None
          puls = None
          chdd = None
          bole = None
          chss = None

          temperature = None
          str_array = []

          if( inform != None ):
            inform_text = name.find_next('p').text

            time = re.findall("\d+\.\d+\.\d+ в \d+\.\d+",inform_text)
            if( len(time)>0 ):
              try:
                time = datetime.datetime.strptime( time[0], '%d.%m.%Y в %H.%M' )
              except ValueError as e:
                time = e
                print(time)
            else:
              time = None

            davleine = re.findall("Артериальное давление \d*/\d*",inform_text)
            if( len(davleine)>0 ):
              davlenie=re.findall(("\d*/\d*"),davleine[0])
              str_array = davlenie[0].split( '/' )
              if( str_array[0] == ''):
                str_array[0] = 0
              if( str_array[1] == ''):
                str_array[1] = 0
              sad = int(str_array[0])
              dad = int(str_array[1])

            if(sad == 0 and dad == 0):
              sad = None
              dad = None

            if( sad == None and dad == None ):

              if( re.search("[Аа][Дд][ -]*\d+[\\\/ и]+\d+",html) ):
                davlenie=re.findall("[Аа][Дд][ -]*\d+[\\\/ и]+\d+",html)[0]
                davlenie=re.findall("\d+[\\\/ и]+\d+",davlenie)[0]
                if( '/' in davlenie ):
                  str_array = davlenie.split( '/' )
                elif( '\\' in davlenie ):
                  str_array = davlenie.split( '\\' )
                elif( ' и ' in davlenie ):
                  str_array = davlenie.split( ' и ' )
                elif( ' ' in davlenie ):
                  str_array = davlenie.split( ' ' )

                if( str_array[0] == ''):
                  str_array[0] = 0
                else:
                  str_array[0] = str_array[0].replace('и','')
                  str_array[0] = str_array[0].replace(' ','')
                sad = int(str_array[0])

                if( len(str_array)>1 ):
                  if( str_array[1] == ''):
                    str_array[1] = 0
                  else:
                    str_array[1] = str_array[1].replace('и','')
                    str_array[1] = str_array[1].replace(' ','')
                  dad = int(str_array[1])

              elif( re.search("[Аа][Дд][ ]*\([систСИСТ]*[/\- ]*[диастДИАСТ]\)[: ]*\d+[\\/ и]+\d+",html) ):
                davlenie=re.findall("[Аа][Дд][ ]*\([систСИСТ]*[/\- ]*[диастДИАСТ]\)[: ]*\d+[\\/ и]+\d+",html)[0]
                davlenie=re.findall("\d+[\\\/ и]+\d+",davlenie)[0]
                if( '/' in davlenie ):
                  str_array = davlenie.split( '/' )
                elif( '\\' in davlenie ):
                  str_array = davlenie.split( '\\' )
                elif( ' и ' in davlenie ):
                  str_array = davlenie.split( ' и ' )
                elif( ' ' in davlenie ):
                  str_array = davlenie.split( ' ' )
                
                if( str_array[0] == ''):
                  str_array[0] = 0
                else:
                  str_array[0] = str_array[0].replace('и','')
                  str_array[0] = str_array[0].replace(' ','')
                sad = int(str_array[0])

                if( len(str_array)>1 ):
                  if( str_array[1] == ''):
                    str_array[1] = 0
                  else:
                    str_array[1] = str_array[1].replace('и','')
                    str_array[1] = str_array[1].replace(' ','')
                  dad = int(str_array[1])
              else:
                sad = None
                dad = None
            
            if( sad == None ):
              sad = re.findall("[СсCc][АаAa][Дд][ :]*\d+",html)
              if( index == 376 ):
                  print(html,sad)
              if( len(sad)>0 ):
                print(sad)
                sad = re.findall("\d+",sad[0])
                sad = int(sad[0])
              else:
                sad = None

            
            if( dad == None ):
              dad = re.findall("[Дд][АаAa][ :]*\d+",html)
              if( len(dad)>0 ):
                dad = re.findall("\d+",dad[0])
                dad = int(dad[0])
              else:
                dad = None
            
            puls = re.findall("Пульс: \d+",inform_text)
            if( len(puls)>0 ):
              puls=re.findall(("\d+"),puls[0])
              if( puls[0] == ''):
                puls[0] = 0
              puls = int(puls[0])
            else:
              puls = None
            
            chdd = re.findall("ЧДД: \d+",inform_text)
            if( len(chdd)>0 ):
              chdd=re.findall(("\d+"),chdd[0])
              if( chdd[0] == ''):
                chdd[0] = 0
              chdd = int(chdd[0])
            else:
              chdd = None

            bole = re.findall("Оценка болевого синдрома по ВАШ \(0-10 баллов\): \d+",inform_text)
            if( len(bole)>0 ):
              bole=re.findall(("\d+"),bole[0])
              if( bole[0] == ''):
                bole[0] = 0
              bole = int(bole[0])
            else:
              bole = None

            temperature = re.findall("Температура: \d*\.\d*",inform_text)
            if( len(temperature)>0 ):
              temperature=re.findall("\d+",temperature[0])
              if( temperature[0] == ''):
                temperature[0] = 0
              temperature = float(temperature[0])
            else:
              temperature = None

            chss = re.findall("[Чч][СсCc][СсCc][: -~–]*\d+",html)

            if( len(chss)>0 ):
              chss=re.findall("\d+",chss[0])
              if( chss[0] == ''):
                chss[0] = 0
              chss = int(chss[0])

            else:
              chss = None

            devZapLechVrach["Дата"][index] = time
            devZapLechVrach["САД"][index] = sad
            devZapLechVrach["ДАД"][index] = dad
            devZapLechVrach["ЧСС"][index] = chss
            devZapLechVrach["Пульс"][index] = puls
            devZapLechVrach["ЧДД"][index] = chdd
            devZapLechVrach["Оценка болевого синдрома по ВАШ"][index] = bole
            devZapLechVrach["Температура"][index] = temperature

          else:
            print( "Error" )

      devZapLechVrach.to_excel(path_PhysicianDiaryEntry,engine='xlsxwriter')
      print( "Разбор документов вида \"Дневниковая запись лечащего врача\" окончен, данные сохранены в таблицу: \n\t\t"+path_PhysicianDiaryEntry )


def get_PhysicianDiaryEntry():
    PhysicianDiaryEntry_df  = get_PhysicianDiaryEntry_docs()
    get_PhysicianDiaryEntry_value( PhysicianDiaryEntry_df )

