import requests 
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from collections import defaultdict
import re
from ast import literal_eval
from time import sleep



"""gets keywords & results before looping through all the pages."""

url = 'https://uk.businessesforsale.com/uk/search?formName=searchForm&keywords=real+Estate+Agencies&newSearch=Search'


user_url = input(f"Please enter your search url, it should broadly mimic the following url:\n{url}\n:")


kw_pat = 'keywords=([^&]*)'
keyword = re.findall(kw_pat,user_url)
print(f"Your Keywords are {re.sub('[+]', ', ', keyword[0])}")


page = requests.get(user_url)
soup = BeautifulSoup(page.text,'html.parser')
nums = soup.find_all('div',class_='num-of-results')[0].text

pat = '(\d+)' # extract numbers
nums_clean = re.findall(pat,nums) # gets max reulst per page and num of results.
total_results = sorted([literal_eval(x) for x in nums_clean])[-1] # extract all results and take largest. 
pages = [i for i in range(1,int(np.ceil(total_results / 25))+1)] # divide results by 25 to get page numbers.

print(f"There are {max(pages)} pages to parse with a total of {total_results} results")

dict_ = defaultdict(list)

for num in pages:
    url = f"https://uk.businessesforsale.com/uk/search/businesses-for-sale-{num}?Keywords={keyword[0]}"
    page = requests.get(url)
    soup = BeautifulSoup(page.text,'html.parser')
    
    for x in soup.find_all('table',class_='result-table'):
        dict_['info'].append((x.find_next('h2').text))
        dict_['location'].append(x.find_next('td').text)

        for fin in x.find_all('tr',class_='t-finance'):
            dict_['ask_price'].append(fin.find_all('td')[0].text)
            dict_['turnover'].append(fin.find_all('td')[1].text)
            dict_['net'].append(fin.find_all('td')[2].text)
        dict_['description'].append(x.find_next('p').text)
        try:
            dict_['additional'].append(x.find_next('li').text)
        except AttributeError:
            dict_['additional'].append(np.nan)
        dict_['page'].append(num)

    sleep(np.random.uniform(0.8,4))
    print(f'{num} of {max(pages)} complete')

df = pd.DataFrame(dict_)
df.replace('\n',' ',regex=True)


