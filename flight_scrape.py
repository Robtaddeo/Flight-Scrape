from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

nyc_url = 'https://skiplagged.com/flights/NYC/2020-02-13/2020-02-16'
nola_url = 'https://skiplagged.com/flights/MSY/2020-02-13/2020-02-16'


# Uses Selenium to open chrome and collect html data from flight site
def get_page_source(url):

    driver = webdriver.Chrome('./chromedriver/chromedriver')
    driver.get(url)
    driver.implicitly_wait(100)
    source = driver.page_source
    driver.quit()
    
    return source

# Helper function that splits city sting from region string after parse
def camel_case_split(str): 
    words = [[str[0]]] 
  
    for c in str[1:]: 
        if words[-1][-1].islower() and c.isupper(): 
            words.append(list(c)) 
        else: 
            words[-1].append(c) 
  
    return [''.join(word) for word in words] 

# From the page source, create a soup object and parse into dataframe
def get_flights_info(out_city, source):
    soup = BeautifulSoup(source, 'html.parser')
    cities = soup.findAll('h2', {'class': 'skipsy-city'})
    regions = soup.findAll('span', {'class': 'skipsy-region'})
    costs = soup.findAll('div', {'class': 'skipsy-cost'})
    
    
    out = []
    for i in range(0, len(cities)):
        try:
            cost = int(costs[i].text[1:])
        except:
            cost = 10000
        
        row = {
            "out_city": out_city,
            "in_city": camel_case_split(cities[i].text)[0],
            "region": regions[i].text,
            "cost": cost
        }
        if(cost < 2000):
            out.append(row)

    df = pd.DataFrame(out)
    df = df[['out_city', "in_city", 'region', 'cost']]
    return df


# Test main, for flights from both NYC and New Orleans
def main():
    nola_souce = get_page_source(nola_url) # New Orleans flight page source
    nyc_source = get_page_source(nyc_url) # New York flight page source
    nyc_df = get_flights_info("New York", nyc_source) # New York flight df
    nola_df = get_flights_info("New Orleans", nola_source) # New orlean flight df

    result = pd.merge(nyc_df, nola_df, on="in_city")
    result.drop(columns=['region_y']) # Merge, drop region column duplicate
    
    result = result[['in_city', 'region_x', 'out_city_x', 'cost_x', 'out_city_y', 'cost_y']]
    result['cost_avg'] = ( result['cost_x'] + result['cost_y'] ) / 2 # adding average column

    result = result.sort_values(by='cost_avg')
    
    export_csv = result.to_csv (r'./df.csv', index = None, header=True) # export into directory
    print(result)
    return result
    
main()


    