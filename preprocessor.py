import numpy as np
import pandas as pd
import re

def preprocess_data(df):
    
    global blacklist_acronym, blacklist_punct, blacklist_char
    blacklist_acronym = ['UAB ', ' UAB', 'AB ', ' AB', 'SIA ', ' SIA', 'VI ', ' VI']
    blacklist_punct = [',', '"', "'"]
    blacklist_char = ['ĄČĘĖĮŠŲŪŽąčęėįšųūž',
                      'ACEEISUUZaceeisuuz']

    preprocess_jobtitle(df)
    preprocess_company(df)
    preprocess_salary(df)
    preprocess_link(df)
    
    print(' >> Preprocessing complete')
    
    return df

def preprocess_jobtitle(df):
    data = df['jobtitle_raw']
    
    letter_mapping = str.maketrans(blacklist_char[0], blacklist_char[1]) # change letters LT -> EN 
    data = data.str.translate(letter_mapping)
    
    data = data.str.upper() # make all upper case
    
    data = data.str.strip() # remove trailing/leading whitespace
    
    while '  ' in data: data = data.replace('  ', ' ') # remove long whitespaces
    
    df['jobtitle'] = data

def preprocess_company(df):
    data = df['company_raw']
    
    letter_mapping = str.maketrans(blacklist_char[0], blacklist_char[1])
    data = data.str.translate(letter_mapping)
    
    blacklist = blacklist_acronym + blacklist_punct # remove blacklisted words
    for blackword in blacklist:
        data = data.str.replace(blackword,'')
    
    data = data.str.strip()
    
    while '  ' in data: data = data.replace('  ', ' ')
   
    df['company'] = data

def preprocess_salary(df):
    data = df['salary_raw']
    
    data_period = data.str.partition(' ')[0]
    period_mapping = {'Valandinis':'Hourly', 'Mėnesinis': 'Monthly', 'Metinis': 'Annual', '0': '0'}
    data_period = data_period.map(period_mapping)
    
    data_mode = np.select([data.str.contains('Fiksuotas ', na=False),
                           (data.str.contains('Nuo ', na=False) & data.str.contains('iki ', na=False)),
                           data.str.contains('Nuo ', na=False),
                           data.str.contains('iki ', na=False)],
                           ['Fix','MinMax','Min','Max'],
                           default='0')
    
    temp_fix = pd.to_numeric(data.str.extract('Fiksuotas ([-+]?\d*\.?\d+|\d+)', expand=False).fillna(0), errors='coerce')
    temp_min = pd.to_numeric(data.str.extract('Nuo ([-+]?\d*\.?\d+|\d+)', expand=False).fillna(0), errors='coerce')
    temp_max = pd.to_numeric(data.str.extract('iki ([-+]?\d*\.?\d+|\d+)', expand=False).fillna(0), errors='coerce')
    
    data_min = np.where(temp_fix == 0, temp_min, temp_fix)
    data_max = np.where(temp_fix == 0, temp_max, temp_fix)
    
    data_min_std = np.where(data_period == 'Hourly', data_min * 160, data_min).round(2)
    data_min_std = data_min.round(2)
    data_min_std = np.where(data_period == 'Annual', data_min / 12, data_min).round(2)
    data_max_std = np.where(data_period == 'Hourly', data_max * 160, data_max).round(2)
    data_max_std = data_max.round(2)
    data_max_std = np.where(data_period == 'Annual', data_max / 12, data_max).round(2)
    
    df['salary_period'] = data_period
    df['salary_mode'] = data_mode
    df['salary_min'] = data_min
    df['salary_max'] = data_max
    df['salary_min_std'] = data_min_std
    df['salary_max_std'] = data_max_std

def preprocess_link(df):
    data = df['link_raw']
    
    data = data.str[2:] # remove two chars '//' from links
    
    data = data.str.strip()
    
    while '  ' in data: data = data.replace('  ', ' ')
        
    df['link'] = data