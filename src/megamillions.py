import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup as bs

def winner_data():
    df = scrape_data()
    df = transformer(df)
    return df

def scrape_data():
    '''
    Scrapes data from megamillions website.  Renders a pandas dataframe.
    '''
    #set lottery url to be scraped
    url = 'https://www.megamillions.com/Winners-Gallery.aspx'
    #get request
    response = requests.get(url)
    #parse html data
    soup = bs(response.text, 'lxml')
    pages = soup.select('div.PagerControl')
    #get the last page of winners
    lst_num =int(pages[0].select('a')[-1:][0]['href'].split('=')[-1])

    names = []

    #loop through all pages and get winner information and amount
    for x in range(1,lst_num+1):
        w_url = url + '?page=' + str(x)
        response = requests.get(w_url)
        soup = bs(response.text, 'lxml')

        name = [x.get_text(strip=True) for x in soup.find_all(class_="winnerListName")]
        location = [x.get_text(strip=True) for x in soup.find_all(class_="winnerListLocation")]
        date = [x.get_text(strip=True) for x in soup.find_all(class_="winnerListDate")]
        amount = [x.get_text(strip=True) for x in soup.find_all(class_="winnerListPrizeAmt")]

        data = pd.DataFrame({
            'name':name,
            'location': location,
            'date':date,
            'amount':amount
            })
        
        names.append(data)
        
    df = pd.concat(names)
    return df

def transformer(df):
    '''
    Transforms pandas dataframe data and creates multiple columns. 
    
    Parameters
    ----------
    dataframe : pandas dataframe
    
    Returns:
    --------
    A dataframe with columns: 'name', 'location', 'date', 'amount', 'unit', 'city', 'state'
    '''
    #split the location column, into city and state
    df[['amount', 'unit']] = df.loc[:,'amount'].apply(lambda x: pd.Series(str(x).split(' ')))
    df[['city', 'state']] = df.loc[:,'location'].apply(lambda x: pd.Series(str(x).split(',')))
    df['amount'] = pd.to_numeric(df.loc[:,'amount'].replace({r'\$': '', ',': ''}, regex=True), downcast='float')
    df['amount'] = [x*1000000 if len(str(np.round(x))) <= 5 else x for x in df['amount']]
    df['unit'] = df.loc[:,'unit'].fillna(value='Thousand')
    df['date'] = pd.to_datetime(df['date'])
    df['state'] =df['state'].apply(lambda x: x.strip())
    df['jackpot'] = df['amount'] >= 40000000
    
    #minor data manipulation; replace Maryland to MD and Mi to MI (webdata is messy no matter the website)
    df['state'].replace({'Maryland':'MD', 'Mi':'MI'}, regex=True, inplace=True)
    
    #create date columns
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['year'] = df['date'].dt.year
    df['dayofweek'] = df['date'].dt.weekday_name
    return df

if __name__ == '__main__':
    winner_data()