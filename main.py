import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#os.chdir('C:\\Users\\Roman\\Desktop\\data science\\job ad scraper')

import scraper
import preprocessor
import gsheets

data = scraper.scrape_data()
data = preprocessor.preprocess_data(data)
gsheets.gsheets_upload(data)

### saving local copy of data
data.to_excel('./data/processed_data_extract.xlsx')
