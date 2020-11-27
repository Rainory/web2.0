from selenium import webdriver
from bs4 import BeautifulSoup
import re


options = webdriver.ChromeOptions()
options.add_argument('headless')

def pars(data, res):
    for i in range(len(data)):
        tds = data[i].find_all('td')
        name = tds[2].find('a').text
        link = 'https://www.finviz.com/' + re.search(r'href=".+"', str(tds[1].find('a'))).group()[6:-1]
        short_name = tds[1].find('a').text
        b_price = float(tds[8].find('a').text)
        res.append([name, link, short_name, b_price])
    return

def get_today():
    # Находим акции с хорошим потенциалом роста, которые просели за последней месяц
    # парсим их с сайта www.finviz.com
    browser = webdriver.Chrome(chrome_options=options)
    url = 'https://www.finviz.com/screener.ashx?v=111&f=cap_midover,fa_debteq_u1,fa_eps5years_o15,fa_pe_u15,ta_perf_4w10u&o=pe'
    browser.get(url)
    html = browser.page_source
    browser.close()
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('tr', {'class': 'table-dark-row-cp'})
    res = []
    pars(data, res)
    data = soup.find_all('tr', {'class': 'table-light-row-cp'})
    pars(data, res)
    return res

def price(s):
    #получаем текущую цену акции
    browser = webdriver.Chrome(chrome_options=options)
    browser.get(s)
    html = browser.page_source
    browser.close()
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find('table', {'class': 'snapshot-table2'})
    data = data.find_all('tr')[10]
    return float(data.find_all('td')[-1].find('b').text)