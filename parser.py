from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from time import sleep
import re


options = webdriver.ChromeOptions()
options.add_argument('headless')
browser = webdriver.Chrome(chrome_options=options)

def get_today():
    # Находим акции с хорошим потенциалом роста, которые просели за последнее время
    url = ''