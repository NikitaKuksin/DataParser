import re
from os import walk, listdir
from bs4 import BeautifulSoup
from tqdm import tqdm
import datetime
import pandas as pd
import numpy as np

from get_name import get_name_history
from get_cod import get_cod_history

path_ProtocolForEstablishingDeath = r'/content/drive/MyDrive/Магистратура/Научная работа/DataSetes/Histores/Docs/Протокол установления смерти человека.xlsx'

def get_ProtocolForEstablishingDeath_doc(text):
    text_reserv = text
    res = [  ]
    doc = "<b>Протокол установления смерти человека</b>"

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
        text = text[index_line[0]:]

    return res

def get_ProtocolForEstablishingDeath_docs():
    table = []
    print( "Загрузка документов вида \"Протокол установления смерти человека\" начата" )

    dead_file = data.loc[ data["Файл(ИБ)"] != "-" ]["Файл(ИБ)"].values

    for file in tqdm(dead_file):
        

        if '.html' not in file:
                continue
        with open(f'{path_HTML_history}/{file}', encoding='utf-8') as file:
                        src = file.read()
        

        soup = BeautifulSoup(src, 'lxml')

        name = get_name_history(soup)
        cod = get_cod_history(soup)

        htmls = get_ProtocolForEstablishingDeath_doc(src)
        

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
    table_df.to_excel(path_ProtocolForEstablishingDeath,engine='xlsxwriter')
    print( "Загрузка документов вида \"Протокол установления смерти человека\" окончена, данные выгружены в таблицу : \n\t\t"+path_ProtocolForEstablishingDeath )
    return table_df
    
def get_ProtocolForEstablishingDeath_values( ProtocolForEstablishingDeath ):
    
    ProtocolForEstablishingDeath["Дата смерти"] = None
    
    for index in tqdm(ProtocolForEstablishingDeath.index):

      if( ProtocolForEstablishingDeath[ "HTML" ][index] != None ):

          html = ProtocolForEstablishingDeath["HTML"][index]
          soup = BeautifulSoup(html, 'lxml')

          dead  = re.findall( "Дата[ _]*\d+\.\d+\.\d+[ _]*Время[ _]*\d+\.\d+[ _]*", html )
          if( len(dead)>0 ):
              data_dead = re.findall( "Дата[ _]*\d+\.\d+\.\d+", dead[0] )
              data_dead = re.findall( "\d+\.\d+\.\d+", data_dead[0] )[0]
              time_dead = re.findall( "Время[ _]*\d+\.\d+", dead[0] )
              time_dead = re.findall( "\d+\.\d+", time_dead[0] )[0]
              #print("test")
              try:
                time_dead = datetime.datetime.strptime( data_dead+" "+time_dead, '%d.%m.%Y %H.%M' )
              except ValueError as e:
                time_dead = e
                print(time_dead)
          else:
            time_dead = "-"

          ProtocolForEstablishingDeath["Дата смерти"][index] = time_dead
    ProtocolForEstablishingDeath.to_excel(path_ProtocolForEstablishingDeath,engine='xlsxwriter')
    

def get_ProtocolForEstablishingDeath(  ):
    ProtocolForEstablishingDeath = get_ProtocolForEstablishingDeath_docs()
    get_ProtocolForEstablishingDeath_values( ProtocolForEstablishingDeath )