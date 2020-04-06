import pandas as pd
import requests
import sys
import sqlite3
from io import StringIO

con = sqlite3.connect("irr.db")

'''
This function will get the closest to zero npv. This will be usefull later for the linear interpolation

df: The dataframe
cost: initial aquisition cost
initial_guess: an initial irr guess 
debug: print debug info
'''
def closestToZero(df, cost, initial_guess, debug):
    #set the precision of the decrement
    precision = 0.9999
    decrement = (cost - cost*precision)/cost
    if debug:
        print('Decrement value: ' + str(decrement))

    while True:
        #Calculate the NPV
        df['pv'] = (1/ pow(1 +  initial_guess, df.index+1 ) ) * df['preco']
        npv = df_assets['pv'].sum() - cost
        if debug:
            print('\nTrying with: ' + str(initial_guess) + ' NPV: ' + str(npv))
           
        #Try to arpoach zero, if npv gets positive returns the closests values
        if npv < 0:
            previous_guess = initial_guess 
            initial_guess = initial_guess - decrement
            previous_npv = npv
        else:
            return {'pos_irr': initial_guess, 'pos_npv': npv, 'neg_npv': previous_npv, 'neg_irr': previous_guess}


selic_url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=csv"
req = requests.get(selic_url)
data = StringIO(req.text)

#format bcb data
df_selic = pd.read_csv(selic_url, ';')
df_selic['valor'] = df_selic['valor'].str.replace(',', '.').astype(float)
df_selic['data'] = pd.to_datetime(df_selic['data'],  format='%d/%m/%Y')
selic_hoje = df_selic['valor'].iloc[0]*100

#read CSV with the assets
if len(sys.argv) <= 1:
    print("Please specify the assets CSV file!")
    sys.exit()
else:
    df_assets = pd.read_csv(sys.argv[1], ';')

df_assets.dropna(how='all', axis='columns', inplace=True)
    
#Format dataframe
df_assets['preco'] =  df_assets['preco'].str.replace(r'(R\$|\.)', '').str.replace(',', '.').astype(float)
df_assets['vencimento'] = pd.to_datetime(df_assets['vencimento'],  format='%d/%m/%Y')

#sort df by date
df_assets.sort_values(by=['vencimento'], inplace=True)

#get de closests npv and discount rates
result = closestToZero(df_assets, 300000.00, 0.08, False)

#Calculates the IRR by linear interoplation
irr = result['pos_irr'] + (( result['pos_npv'] / ( result['pos_npv'] - result['neg_npv']) ) * (result['neg_irr'] - result['pos_irr']))

print("\n IRR: {:.2f}%".format(irr*100))
print("\n Selic today: {:.2f}%" .format(selic_hoje))

print(" Saving data into sqlite...")
df_assets.to_sql("assets", con, if_exists="replace")
df_selic.to_sql("selic", con, if_exists="replace")

assets = pd.read_sql_query("SELECT * from assets", con)




