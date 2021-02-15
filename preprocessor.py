import numpy as np
import re

def preprocess_data(df):
    df['jobtitle'] = df['jobtitle_raw'].str.strip() # remove white space (trailing and leading)
    df['company'] = df['company_raw'].str.strip()
    df['salary'] = df['salary_raw'].str.strip()
    df['link'] = df['link_raw'].str.strip()
    
    df['jobtitle'] = df['jobtitle'].str.upper() # make all upper case
    
    blacklist = ['UAB', 'AB', 'SIA', '"', "'", '(', ')', ','] # remove punctuation and legal entity acronyms (UAB, AB, ...)
    for i in range(df.shape[0]):
        for blackword in blacklist:
            df.at[i, 'company'] = df.at[i, 'company'].replace(blackword, '')
    df['company'] = df['company'].str.strip()
    
    letters_bad = ['Ą','Č','Ę','Ė','Į','Š','Ų','Ū','ą','č','ę','ė','į','š','ų','ū','ž'] # change LT letters to EN analogues
    letters_good = ['A','C','E','E','I','S','U','U','a','c','e','e','i','s','u','u','z']
    for i in range(df.shape[0]):
        for char in letters_bad:
            if char in df['company']:
                df.at[i,'company'] = df.at[i,'company'].replace(char, letters_good[letters_bad.index(char)])
            if char in df['jobtitle']:
                df.at[i,'jobtitle'] = df.at[i,'jobtitle'].replace(char, letters_good[letters_bad.index(char)])
        df.at[i, 'company'] = re.sub(' +', ' ', df.at[i, 'company']) # remove long whitespaces
        df.at[i, 'jobtitle'] = re.sub(' +', ' ', df.at[i, 'jobtitle'])
    
    for i in range(df.shape[0]):
        df.at[i, 'salary_period'] = df.at[i, 'salary'].partition(' ')[0] # get first word of string, encoded as utf-8
        df.at[i, 'salary_period'] = df.at[i, 'salary_period'].replace("Valandinis", "Hourly").replace("Mėnesinis", "Monthly").replace("Metinis", "Annual")
        
        if ("Fiksuotas" in df.at[i, 'salary']):
            df.at[i, 'salary_mode'] = "Fixed"
            df.at[i, 'salary_min'] = float(re.findall(r"[-+]?\d*\.\d+|\d+", df.at[i, 'salary'])[0]) # get all numbers(list), take 1st element
            df.at[i, 'salary_max'] = float(re.findall(r"[-+]?\d*\.\d+|\d+", df.at[i, 'salary'])[0]) # get all numbers(list), take 1st element
        elif ("Nuo" in df.at[i, 'salary']) and ("iki" in df.at[i, 'salary']):
            df.at[i, 'salary_mode'] = "IntervalMinMax"
            df.at[i, 'salary_min'] = float(re.findall(r"[-+]?\d*\.\d+|\d+", df.at[i, 'salary'])[0])
            df.at[i, 'salary_max'] = float(re.findall(r"[-+]?\d*\.\d+|\d+", df.at[i, 'salary'])[1]) # get all numbers(list), take 2nd element
        elif ("Nuo" in df.at[i, 'salary']):
            df.at[i, 'salary_mode'] = "IntervalMin"
            df.at[i, 'salary_min'] = float(re.findall(r"[-+]?\d*\.\d+|\d+", df.at[i, 'salary'])[0])
            df.at[i, 'salary_max'] = np.nan
        elif ("iki" in df.at[i, 'salary']):
            df.at[i, 'salary_mode'] = "IntervalMax"
            df.at[i, 'salary_min'] = np.nan
            df.at[i, 'salary_max'] = float(re.findall(r"[-+]?\d*\.\d+|\d+", df.at[i, 'salary'])[0])
        else:
            df.at[i, 'salary_mode'] = "-1"
            df.at[i, 'salary_min'] = np.nan
            df.at[i, 'salary_max'] = np.nan
        
        if df.at[i, 'salary_period'] == "Hourly": # standardize salary rates to base month
            df.at[i, 'salary_min_std'] = round(df.at[i, 'salary_min'] * 160, 2)
            df.at[i, 'salary_max_std'] = round(df.at[i, 'salary_max'] * 160, 2)
        elif df.at[i, 'salary_period'] == "Monthly":
            df.at[i, 'salary_min_std'] = round(df.at[i, 'salary_min'], 2)
            df.at[i, 'salary_max_std'] = round(df.at[i, 'salary_max'], 2)
        elif df.at[i, 'salary_period'] == "Annual":
            df.at[i, 'salary_min_std'] = round(df.at[i, 'salary_min'] / 12, 2)
            df.at[i, 'salary_max_std'] = round(df.at[i, 'salary_max'] / 12, 2)
        
        df.at[i, 'link'] =  re.sub(r'^.*?www', 'www', str(df.at[i, 'link_raw'])) # remove characters before 'www'
    
    print(' >> Preprocessing complete')
    
    return df