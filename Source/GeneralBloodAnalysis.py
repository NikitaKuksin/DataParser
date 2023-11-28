
import sys
path_source_cod = r'/content/drive/MyDrive/Магистратура/Научная_работа/Parser/Source/'
sys.path.append(path_source_cod)

from constants import path_GeneralBloodAnalysis, path_HTML_analiz
from get_name import get_name_history
from get_cod import get_cod_history

import re
from os import walk, listdir
from bs4 import BeautifulSoup
from tqdm import tqdm
import datetime
import pandas as pd
import numpy as np

#------------------------------------------------------------------------------------Выгрузка документов вида "Общий анализ крови" и "Общий анализ крови-экспрес"

def get_GeneralBloodAnalysis_docs():
    table = []
    print( "Загрузка документов вида \"Общий анализ крови\" и \"Общий анализ крови-экспрес\" начата" )

    for file in tqdm(listdir(path_HTML_analiz)):
        if '.html' not in file:
                continue
        with open(f'{path_HTML_analiz}/{file}', encoding='utf-8') as file:
                        src = file.read()

        htmls = get_GeneralBloodAnalysis_doc(src,"<b>Общий анализ крови</b>","Общий анализ крови")
        
        htmls_e = get_GeneralBloodAnalysis_doc(src,"<b>Общий анализ крови_экспресс</b>","Общий анализ крови_экспресс")
        
        name = None
        if( len(htmls) > 0 and htmls[0]["Name"]!="-" ):
            name = htmls[0]["Name"]
        elif( len(htmls_e) > 0 and htmls_e[0]["Name"]!="-" ):
            name = htmls_e[0]["Name"]
        
        cod = None
        if( len(htmls) > 0 and htmls[0]["Cod"]!="-" ):
            cod = htmls[0]["Cod"]
        elif( len(htmls_e) > 0 and htmls_e[0]["Cod"]!="-" ):
            cod = htmls_e[0]["Cod"]
        
        if( len(htmls) > 0 and htmls[0] != None ):
          for html in htmls :
            table.append({
                    "File Name": file.name,
                    "Name": name,
                    "Cod": cod,
                    "HTML": html["HTML"],
                    "Doc": html["Doc"],
                    "Find": "Да",
                })
        else:
          table.append({
                    "File Name": file.name,
                    "Name": name,
                    "Cod": cod,
                    "HTML": "-",
                    "Doc": "Общий анализ крови",
                    "Find": "Нет",
                })

        if( len(htmls_e) > 0 and htmls_e[0] != None ):
          
          for html in htmls_e :
            table.append({
                    "File Name": file.name,
                    "Name": name,
                    "Cod": cod,
                    "HTML": html["HTML"],
                    "Doc": html["Doc"],
                    "Find": "Да",
                })
        else:
          table.append(
                {
                    "File Name": file.name,
                    "Name": name,
                    "Cod": cod,
                    "HTML": "-",
                    "Doc": "Общий анализ крови_экспресс",
                    "Find": "Нет",
                }  
                )

    table_df = pd.DataFrame( table )
    table_df.to_excel(path_GeneralBloodAnalysis,engine='xlsxwriter')
    print( "Загрузка документов вида \"Общий анализ крови\" и \"Общий анализ крови-экспрес\" окончена, данные выгружены в таблицу : \n\t\t"+path_GeneralBloodAnalysis )
    return table_df

def get_GeneralBloodAnalysis_doc(text,find_string,doc):
    
    res = [  ]

    while ( text.find(find_string) != -1  ):
      index_beging = text.find(find_string)
      if( index_beging == -1 ):
        return None
      text = text[index_beging:]

      iter_line = re.finditer("<hr style=\"color:green;\">",text)
      index_line = []
      for i in iter_line:
        index_line.append( i.start() )

      if( len(index_line)>0 ):
        
        html = text[:index_line[0]]
        
        soup = BeautifulSoup(html, 'lxml')
        name = soup.find('i')
        if( name != None ):
          name = name.text
          fio = re.findall( "[А-ЯЁA-Z]", name )
          if( len(fio) == 2 ):
            name = name.split(" ")
            name = name[0]+" "+fio[1]
          elif( len(fio) == 3 ):
            name = name.split(" ")
            name = name[0]+" "+fio[1]+fio[2]
          else:
            name = "-"
        
        cod = soup.find('b',string = re.compile( "Медицинская карта №" ) )
        if( cod != None ):
          cod = cod.find_next( "i" ).text
          cod = re.findall( "\d+", cod )[0]
        else:
          cod = "-"
        res.append( 
                    {
                      "Name":name,
                      "Cod":cod,
                      "HTML":html,
                      "Doc":doc
                    }
             )
        text = text[index_line[0]:]
      else:
        res.append( 
                    {
                      "Name":"-",
                      "Cod":"-",
                      "HTML":"Конец документа не обнаружен",
                      "Doc":doc
                    }
             )
        break

    return  res
    
#------------------------------------------------------------------------------------Выгрузка документов вида "Общий анализ крови" и "Общий анализ крови-экспрес"


def get_GeneralBloodAnalysis_values( GeneralBloodAnalysis ):

    GeneralBloodAnalysis["Время выполнения"] = "-"
    GeneralBloodAnalysis["Дата направления"] = "-"
    GeneralBloodAnalysis["Дата взятия биоматериала"] = "-"

    for index in tqdm(GeneralBloodAnalysis.index):

      if( GeneralBloodAnalysis[ "Find" ][index] == "Да" ):
          #print( GeneralBloodAnalysis["HTML"][index] )
          html = GeneralBloodAnalysis["HTML"][index]
          soup = BeautifulSoup(html, 'lxml')

          time_lead  = re.findall( "Выполнен \d+\.\d+\.\d+ в \d+:\d+", html )
          if( len(time_lead)>0 ):
              time_lead  = re.findall( "\d+\.\d+\.\d+ в \d+:\d+", time_lead[0] )
              try:
                time_lead = datetime.datetime.strptime( time_lead[0], '%d.%m.%Y в %H:%M' )
              except ValueError as e:
                time_lead = e
                print(time_lead)
          else:
            time_lead = "-"

          time_referral = soup.find( "b", string = re.compile( "Дата направления" ) )
          if( time_referral != None ):
            time_referral = time_referral.find_next( "i" )
            if( time_referral ):
              try:
                time_referral = datetime.datetime.strptime( time_referral.text, '%d.%m.%Y в %H:%M' )
              except ValueError as e:
                time_referral = e
                print(time_referral)
            else:
              time_referral = "-"
          else:
            time_referral = "-"
          
          date_sampling = soup.find( "b", string = re.compile( "Дата взятия биоматериала" ) )
          if( date_sampling != None ):
            date_sampling = date_sampling.find_next( "i" )
            if( date_sampling ):
              date_sampling = date_sampling.text
            else:
              date_sampling = None
          else:
            date_sampling = None

          time_sampling = soup.find( "b", string = re.compile( "Время" ) )
          if( time_sampling != None ):
            time_sampling = time_sampling.find_next( "i" )
            if( time_sampling ):
              time_sampling = time_sampling.text
            else:
              time_sampling = None
          else:
            time_sampling = None


          if( date_sampling != None and time_sampling != None ):
            try:
                time_sampling = datetime.datetime.strptime( date_sampling+" "+time_sampling, '%d.%m.%Y %H:%M' )
            except ValueError as e:
                time_sampling = e
                print(time_sampling)
          else:
            time_sampling = "-"

          GeneralBloodAnalysis["Время выполнения"][index] = time_lead
          GeneralBloodAnalysis["Дата направления"][index] = time_referral
          GeneralBloodAnalysis["Дата взятия биоматериала"][index] = time_sampling

    GeneralBloodAnalysis.to_excel(path_GeneralBloodAnalysis,engine='xlsxwriter')


def get_GeneralBloodAnalysis(  ):
    GeneralBloodAnalysis_df = get_OperationProgress_docs()
    get_GeneralBloodAnalysis_value( GeneralBloodAnalysis_df )

