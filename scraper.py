import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_data():
    df = pd.DataFrame(columns = ['jobtitle_raw',
                                 'company_raw',
                                 'salary_raw',
                                 'link_raw'])
    page_nr = -1
    
    while True:
        page_nr += 1
        
        url = 'https://www.cvonline.lt/darbo-skelbimai/vilniaus?page=' + str(page_nr)
        page = requests.get(url)
        print(' >> Scraping page number: ', '{:>4}'.format(page_nr), 
              ' | Returned request status code: ', '{:>4}'.format(page.status_code))
        
        if page.status_code != 200: # break loop if returned request status code not 200 (=page unavailable)
            print(' >> Reached last page, terminating loop', 
                  ' | Returned request status code: ', '{:>4}'.format(page.status_code))
            break
        
        soup = BeautifulSoup(page.text, 'html.parser')
        ad_page = soup.find(class_='cvo_module_offers_wrap')
        ad_box = ad_page.find_all(class_="offer_primary_info")
        ad_total = len(ad_box) # total nr of ads for currently soup'ed page
        
        for ad_nr in range(ad_total):
            ad = ad_box[ad_nr]
            
            jobtitle = ad.find(itemprop="title").get_text()
            company = ad.find(itemprop="name").get_text()
            if ad.find(class_="salary-blue") is None: # if salary not given
                salary = "-1"
            else:
                salary = ad.findAll(class_="salary-blue") # block may contain not only salary, but other info
                if len(salary) == 1: # if contains only salary (1 element), save it
                    salary = ad.find(class_="salary-blue").get_text()
                else: # if contains not only salary (>1 element), save second element (salary)
                    salary = salary[1].get_text()
            link = ad.find("a")['href']
            
            df = df.append({'jobtitle_raw': jobtitle,
                                  'company_raw': company,
                                  'salary_raw': salary,
                                  'link_raw': link}, ignore_index=True)
    
    return df