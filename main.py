import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#os.chdir('local\\directory')

import scraper
import preprocessor
import loader

data = scraper.scrape_data()
data = preprocessor.preprocess_data(data)
loader.gsheets_upload(data)

### saving local copy of data
data.to_excel('./data/processed_data_extract.xlsx')