
import re
from bs4 import BeautifulSoup

def get_cod_history(soup):

    cod = soup.find('b', string="   № истории ")
    if( cod != None ):
      res = cod.find_next('span').text
      res = res.replace( " ", "" )
      return res
    
    cod = soup.find('h4',string = "Первичный врачебный осмотр") 
    if( cod != None ):
      res = cod.find_next('i')
      res = res.find_next('i')
      res = res.find_next('i').text
      return res

    cod = soup.find('b',string = "Дневниковая запись лечащего врача") 
    if cod != None:
      res = cod.find_next('font').text
      cod = res.split("\xa0")
      if( len(cod) == 6 ):
          res = cod[3]
          cod = re.findall( "[0123456789\-]+",res )
          if( len(cod) > 0 ):
            res = cod[0]
      return res 
      
      
      
def get_cod_analiz(soup):

    cod = soup.find('b', string="   № истории ")
    if( cod != None ):
      res = cod.find_next('span').text
      res = res.replace( " ", "" )
      return res
    
    cod = soup.find('h4',string = "Первичный врачебный осмотр") 
    if( cod != None ):
      res = cod.find_next('i')
      res = res.find_next('i')
      res = res.find_next('i').text
      return res

    cod = soup.find('b',string = "Дневниковая запись лечащего врача") 
    if cod != None:
      res = cod.find_next('font').text
      cod = res.split("\xa0")
      if( len(cod) == 6 ):
          res = cod[3]
          cod = re.findall( "[0123456789\-]+",res )
          if( len(cod) > 0 ):
            res = cod[0]
      return res 