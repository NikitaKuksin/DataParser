
import sys
path_source_cod = r'/content/drive/MyDrive/Магистратура/Научная_работа/Parser/Source/'
sys.path.append(path_source_cod)

from constants import path_UltrasoundExaminationOfHeart, path_HTML_history
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

def get_UltrasoundExaminationOfHeart_docs():
    table = []
    print( "Загрузка документов вида \"Ультрозвуковое исследование сердца\" начата" )
    for file in tqdm(listdir(path_HTML_history)):
        
        if '.html' not in file:
                continue
        with open(f'{path_HTML_history}/{file}', encoding='utf-8') as file:
                        src = file.read()
        
        soup = BeautifulSoup(src, 'lxml')
        print(file.name)
        name = get_name_history(soup)
        cod = get_cod_history(soup)

        htmls = get_UltrasoundExaminationOfHeart_doc(src)
        
        

        if( len(htmls) > 0 ):
                  
                  for html in htmls :
                    if( html == "Ошибка"):
                      find = "Ошибка"
                    else:
                      find = "Да"

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
                  find = "Нет"
                  table.append(
                        {
                            "File Name": file.name,
                            "Name": str(name),
                            "Cod": str(cod),
                            "Find": find,
                            "HTML": None,
                        }
                )
        break
    
    table_df = pd.DataFrame( table )
    table_df.to_excel(path_UltrasoundExaminationOfHeart,engine='xlsxwriter')
    print("Загрузка документов вида \"Ультрозвуковое исследование сердца\" окончена, данные выгружены в таблицу : \n\t\t"+path_UltrasoundExaminationOfHeart) 
    return table_df


def get_UltrasoundExaminationOfHeart_doc(text):
    text_reserv = text
    res = [  ]
    doc = "<h4>УЛЬТРАЗВУКОВОЕ ИССЛЕДОВАНИЕ СЕРДЦА </h4>"
    doc2 = "<h4> УЛЬТРАЗВУКОВОЕ ИССЛЕДОВАНИЕ СЕРДЦА </h4>"

    print(text,text.find(doc))


    while ( text.find(doc) != -1 or text.find(doc2) != -1 ):


      index_beging = text.find(doc)
      if( index_beging == -1 ):
        index_beging = text.find(doc2)
      
      text = text[index_beging:]

      iter_line = re.finditer("<h4>",text)
      index_line = []
      for i in iter_line:
        index_line.append( i.start() )

      if( len(index_line) == 1 ):
        
        iter_line = re.finditer("</p>",text)
        index_line = []
        for i in iter_line:
          index_line.append( i.start() )
        

        if( len(index_line)>=0 ):
          
          print(text[:index_line[0]] )
          res.append( text[:index_line[0]] )


          text = text[index_line[0]:]
        else:
          res.append( "Ошибка" )
          break
      else:
        if( len(index_line)>=2 and index_line[1]<4000 ):

          #print(index_line[1])
          res.append( text[:index_line[1]] )
          text = text[index_line[1]:]
        else:
          res.append( "Ошибка" )
          text = text[index_line[1]:]

    return res
    
#------------------------------------------------------------------------------------Выгрузка документов вида "Общий анализ крови" и "Общий анализ крови-экспрес"


def get_UltrasoundExaminationOfHeart_value( UltrasoundExaminationOfHeart ):
    
    print( "Разбор документов вида \"Ультрозвуковое исследование сердца\" начат" )

    UltrasoundExaminationOfHeart["ЛЖ/Ао"] = None
    UltrasoundExaminationOfHeart["АоС"] = None
    UltrasoundExaminationOfHeart["АоС в заключении"] = None

    for index in tqdm(UltrasoundExaminationOfHeart.index):
        html = UltrasoundExaminationOfHeart["HTML"][index]
        if( type(html) == float ):
            continue

        html = html.replace("&nbsp;"," ")
        davlenie  = None
        aoc  = None
        zak = None
        
        #---------------------------------------------------------------------------ЛЖ/Ао
        if( re.search( "ЛЖ/Ао[ ]*\d+[ ]*мм\.рт\.ст\.", html) ):
            davlenie = re.findall( "ЛЖ/Ао[ ]*\d+[ ]*мм\.рт\.ст\.", html)
            davlenie = int(re.findall( "\d+", davlenie[0])[0])
            if( davlenie>=15 ):
              aoc = "Да"
            else:
              aoc = "Нет"
        elif( re.search( "ЛЖ/Ао[ ]*\d+[\.,]\d+[ ]*мм\.рт\.ст\.", html) ):
            #print("Test")
            davlenie = re.findall( "ЛЖ/Ао[ ]*\d+[\.,]\d+[ ]*мм\.рт\.ст\.", html)
            davlenie = float(re.findall( "\d+[\.,]\d+", davlenie[0])[0].replace( ",","." ))
            if( davlenie>=15 ):
              aoc = "Да"
            else:
              aoc = "Нет"
        else:
          davlenie = "-"
          aoc = "-"
          
        #---------------------------------------------------------------------------Заключение

        if( re.search( "Заключение[ ]*:", html) ):
            zak = re.findall( "Заключение[ ]*:", html)[0]

            iter_line = re.finditer(zak,html)
            index_line = []
            for i in iter_line:
              zak = html[i.start():]
              zak = zak.lower()
              zak = re.findall( "[aа][oо][cс]|стеноз[ ]*аортальн[ого]*[ ]*клапан[а]*", zak)
              if( len(zak) > 0 ):
                zak = "Да"
              else:
                zak = "Нет"
        else:
          zak = "-"

        UltrasoundExaminationOfHeart["ЛЖ/Ао"][index] = davlenie
        UltrasoundExaminationOfHeart["АоС"][index] = aoc
        UltrasoundExaminationOfHeart["АоС в заключении"][index] = zak

    UltrasoundExaminationOfHeart.to_excel(path_UltrasoundExaminationOfHeart,engine='xlsxwriter')
    print( "Разбор документов вида \"Ультрозвуковое исследование сердца\" окончен, данные сохранены в таблицу: \n\t\t"+path_UltrasoundExaminationOfHeart )


def get_UltrasoundExaminationOfHeart(  ):
    UltrasoundExaminationOfHeart_df = get_UltrasoundExaminationOfHeart_docs()
    get_UltrasoundExaminationOfHeart_value( UltrasoundExaminationOfHeart_df )

