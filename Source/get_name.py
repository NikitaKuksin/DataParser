
import re
from bs4 import BeautifulSoup


def get_name_history(soup):  

    fio = soup.find('b', string="ФИО больного ")
    if fio != None:
      res = fio.find_next('span').text
      res = res.replace( " ", "" )
      res = res.replace( ".", "" )
      N_O = re.findall( "[A-ZА-ЯЁ]+",res )
      if( len(N_O) >= 2 ):
        index = res.find( N_O[1] )
        res = res[:index] + " " + res[index:]
      return res

    fio = soup.find('h4',string = "Первичный врачебный осмотр") 
    if fio != None:
      res = fio.find_next('h4').text
      fio = res.split("\xa0")
      if( len(fio) == 2 ):
          res = fio[0]+ " " +fio[1][0]
      elif ( len(fio) == 3 ):
          res = fio[0]+ " " + fio[1][0]+fio[2][0]
      return res

    fio = soup.find('b',string = "Дневниковая запись лечащего врача") 
    if fio != None:
      res = fio.find_next('font').text
      fio = res.split("\xa0")
      if( len(fio) == 6 ):
          res = fio[1]
          res = res.replace( " ", "" )
          res = res.replace( ".", "" )
          N_O = re.findall( "[A-ZА-ЯЁ]+",res )
          if( len(N_O) >= 2 ):
            index = res.find( N_O[1] )
            res = res[:index] + " " + res[index:]
      return res 
      

def get_name_analiz(soup):  

    fio = soup.find('b', string="ФИО больного ")
    if fio != None:
      res = fio.find_next('span').text
      res = res.replace( " ", "" )
      res = res.replace( ".", "" )
      N_O = re.findall( "[A-ZА-ЯЁ]+",res )
      if( len(N_O) >= 2 ):
        index = res.find( N_O[1] )
        res = res[:index] + " " + res[index:]
      return res

    fio = soup.find('h4',string = "Первичный врачебный осмотр") 
    if fio != None:
      res = fio.find_next('h4').text
      fio = res.split("\xa0")
      if( len(fio) == 2 ):
          res = fio[0]+ " " +fio[1][0]
      elif ( len(fio) == 3 ):
          res = fio[0]+ " " + fio[1][0]+fio[2][0]
      return res

    fio = soup.find('b',string = "Дневниковая запись лечащего врача") 
    if fio != None:
      res = fio.find_next('font').text
      fio = res.split("\xa0")
      if( len(fio) == 6 ):
          res = fio[1]
          res = res.replace( " ", "" )
          res = res.replace( ".", "" )
          N_O = re.findall( "[A-ZА-ЯЁ]+",res )
          if( len(N_O) >= 2 ):
            index = res.find( N_O[1] )
            res = res[:index] + " " + res[index:]
      return res 