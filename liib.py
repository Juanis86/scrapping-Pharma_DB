import re
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
import time
import concurrent.futures
import threading
import requests
from bs4 import BeautifulSoup, SoupStrainer
import datetime as dtime
from urllib.parse import urljoin
from datetime import datetime
session = requests.Session()
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from selenium.webdriver import ActionChains
import os
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
directorio_actual = os.path.dirname(__file__)


def set_driver(country):
    ruta_descargas = os.path.dirname(__file__)+ f'/dataset/{country}' 
    print(ruta_descargas)
    opciones = Options()
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-dev-shm-usage')
    opciones.add_argument('--disable-gpu')
    opciones.add_argument('--window-size=1920,1080')
    #opciones.add_argument('--headless')  
    prefs = {
        'download.default_directory': ruta_descargas,  
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    }
    opciones.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opciones)
    return driver


#Austria

def get_med_Austria(country):
    driver= set_driver(country)
    Austria = 'https://aspregister.basg.gv.at/aspregister/faces/aspregister.jspx'
    time.sleep(50)
    driver.get(Austria)

    elemento = driver.find_element(By.XPATH, '//*[@id="cb1"]')
    elemento.click()
    time.sleep(25)

    elemento = driver.find_element(By.XPATH, '//*[@id="pc1:ctb1"]/a')
    print(elemento)
    print('click')
    elemento.click()
    time.sleep(25)
    df = pd.read_excel('proyectos/BD_Medicamentos_aprovados/dataset/Austria/ASP-Register.xlsx')
    for c in df['Zulassungsnummer']:
        url_descarga = "https://aspregister.basg.gv.at/document/servlet?action=show&zulnr={}&type=DOTC_GEBR_INFO".format(c)
        driver.get(url_descarga)
        url_descarga = "https://aspregister.basg.gv.at/document/servlet?action=show&zulnr={}&type=DOTC_FATCH_INFO".format(c)
        driver.get(url_descarga)

#Argentina
def get_labs_Argentina():
   driver= set_driver('Argentina')
   df_tot=pd.DataFrame([])
   driver.get('https://servicios.pami.org.ar/vademecum/views/consultaPublica/listado.zul')
   driver.find_element(By.XPATH, ('//a[@id="zk_comp_40-btn"]')).click()
   time.sleep(2)
   html= driver.page_source
   pages= BeautifulSoup(html, 'html.parser')
   pages= pages.find_all('span', {'class': 'class="z-paging-text"'})
   print(pages)
   n=0
   acciones = ActionChains(driver)
   for p in range(42):
           time.sleep(0.5)
           html= driver.page_source
           df= pd.read_html(html)
           df_tot= pd.concat([df_tot, df[9]],ignore_index=True)

           print(df_tot)
           print(n)
           element= driver.find_element(By.NAME, ('zk_comp_61-real'))
           if n==1:
               acciones.double_click(element).perform()
               element.send_keys(Keys.SUBTRACT)
               element.send_keys(n)
               element.send_keys(Keys.ENTER)
           else:
               element= driver.find_element(By.NAME, ('zk_comp_61-next')).click()
           n+=1
   print(df_tot)
   df_tot= pd.DataFrame(df_tot)
   df_tot.columns=['CUIT', 'GLN', 'Razon_social']
   df_tot=df_tot.dropna()
   df_tot= df_tot.astype({"CUIT":'int64',"GLN":'int64'})
   df_tot.to_csv('labos_arg.csv')



#Belgica

def get_med_Belgica():
    response = requests.get('https://banquededonneesmedicaments.fagg-afmps.be/download/documents')

    # Verificar si la solicitud fue exitosa (código de respuesta 200)
    if response.status_code == 200:
        # Obtener el contenido del archivo
        contenido = response.content

        # Guardar el contenido en un archivo local
        nombre_archivo = 'Belgica.csv'  # Nombre deseado para el archivo
        with open(nombre_archivo, 'wb') as archivo:
            archivo.write(contenido)
    df = pd.read_csv('Belgica.csv', sep=';', header=0)
    for index, row in df.iterrows():
        for n in range(9, len(df.columns)):
            if 'https://app.fagg-afmps.be/pharma-status/api/files' in str(row[n]):
                response = requests.get(row[n])
                if response.status_code == 200:
                    filename = 'Belgica'+re.sub(r"[\/:*?\"<>|]", "", row[4]) + ".pdf"
                    with open(filename, 'wb') as archivo:
                        archivo.write(response.content)
                    break
            else:
                pass

#Bulgaria

def get_med_Bulgaria():
    df_tot=[]
    for i in range(ord('A'), ord('Z')+1):
        letter = chr(i)    
        url = f'https://www.bda.bg/images/stories/documents/bdias/{letter}-1.htm'
        tables = pd.read_html(url)
        df = tables[0]
        df = df.iloc[5:]
        df= df.iloc[:, :3]
        df.columns= ['trade_name', 'active', 'number']
        df_tot= pd.concat([pd.DataFrame(df_tot), df])
        for url in [url, f'https://www.bda.bg/images/stories/documents/bdias/{i}-2.htm']:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a')
            link_urls = []
            for link in links:
                link_url = link.get('href')
                response = requests.get('https://www.bda.bg/images/stories/documents/bdias/'+link_url)
                filename = 'Bulgaria'+link_url.split('/')[-1] + ".pdf"
                with open(filename, 'wb') as archivo:
                    archivo.write(response.content)
    df_tot.to_csv('Bulgaria.csv', index=False)

#Croacia

def get_med_croacia():
    driver = set_driver('Croacia')
    driver.get("https://www.halmed.hr/en/Lijekovi/Baza-lijekova/#rezultati")
    search_input = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/div[1]/div[2]/article/div/div/form/div[2]/div[2]/div[2]").click()
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href= True)
    link_urls = []
    for l in links:
       l= str(l).split('"')[1]
       if '/en/Lijekovi/Baza-lijekova' in l:
           link_urls.append('https://www.halmed.hr'+l)
    for link in link_urls:
        driver.get(link)
        links_totals = []
        dic = {}
        rows = driver.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            row_data = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
            col_data = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "th")]
            for c in col_data:
                for r in row_data:
                    dic[c] = r
        dld = driver.page_source
        soup= BeautifulSoup(dld,  'html.parser')
        download_links = soup.find_all("a", string="download")
        download_urls = [link["href"] if 'pdf' in link['href'] else None for link in download_links]
        download_urls= list(filter(None, download_urls))
        for pdf in download_urls:
            try:
                response = requests.get('https://www.halmed.hr'+pdf)
                if response.status_code == 200:
                        filename = 'Croacia'+re.sub(r"[\/:*?\"<>|]", "", pdf) + ".pdf"
                        with open(filename, 'wb') as archivo:
                            archivo.write(response.content)
                        break
                else:
                    pass
            except:
                pass

def get_med_Dinamarca():
    url= f'https://www.produktresume.dk/AppBuilder/search'
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
       # Obtener el contenido de la página
       html = response.content
       n=0
       soup = BeautifulSoup(html, 'lxml')
       links = soup.find_all('a')
       while len(links) > 0:
            for link in links:
                print(link)
                # Obtener el nombre del archivo de la URL
                parsed_url = urlparse.urlparse(link)
                filename = os.path.basename(parsed_url.path)
                response = requests.get(link)
                if response.status_code == 200:
                    with open(filename, 'wb') as file:
                        file.write(response.content)
                        print(f"Archivo descargado: {filename}")
                else:
                    print(f"No se pudo descargar el archivo: {filename}")
            n+=1
            url= f'https://www.produktresume.dk/AppBuilder/search?page={n}'
            response = requests.get(url)

if __name__ == '__main__':
   #get_med_Austria('Austria')
   #get_med_Belgica()
   #get_med_Bulgaria()
   #get_med_Croacia()
   #get_med_Dinamarca()
   #get_labs_Argentina()
        
