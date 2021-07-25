from django.shortcuts import render

from django.contrib import messages
from django.http import HttpResponse
import requests

import pandas as pd

# Create your views here.

def about(request):
  return render(request,'report/about.html',context = {'name' : 'Guru','title': 'About'})


def generate_rpt(request):
    if request.method == 'POST':
        file_name = request.FILES.get('csv_file') 
        if file_name :
          if allowed_files(file_name):
            df = pd.read_csv(request.FILES.get('csv_file')) 
            try:
              coin,chart_values,table_data = file_processing(df)
              data = {
                'Coin':coin,
                'chart_values':chart_values,
                'table_data':table_data
              }
              return render(request,'report/report.html',context = data)
            except :
              messages.warning(request, "Unable to process the file")
              return render(request,'report/upload.html')
          else:
            messages.warning(request, "Plese upload a CSV file")
            return render(request,'report/upload.html')
    else:
        return render(request,'report/upload.html')


# Data processing from the file

def file_processing(df):
  df = df[df['Status'] == 'filled']
  coin_list = list(df['Market'].unique())
  response = requests.get("https://api.coindcx.com/exchange/ticker")
  current_price = {}

# Get current market price
  for i in (response.json()):
    if i['market'] in coin_list:
      current_price[i['market']] = i['last_price']

  result_dict = {}
  for i in coin_list:
    sell_sum = 0
    buy_sum = 0
    buy_quant = 0
    sell_quant = 0
    df_temp = df[(df['Market'] == i)].reset_index()

    for row in range(0,len(df_temp)):
      if df_temp.loc[row]['Side'] == 'sell':
        sell_sum += (df_temp.loc[row]['Total Quantity']) * (df_temp.loc[row]['Avg Price'])
        sell_quant += df_temp.loc[row]['Total Quantity']
      if df_temp.loc[row]['Side'] == 'buy':
        buy_sum += (df_temp.loc[row]['Total Quantity']) * (df_temp.loc[row]['Avg Price'])
        buy_quant += df_temp.loc[row]['Total Quantity']

    if buy_quant-sell_quant >0:
      avg_unit_price = (buy_sum - sell_sum)/(buy_quant-sell_quant)
      PnL_precentage = ((float(current_price[i]) - avg_unit_price )/ float(current_price[i])) * 100
    else:
      avg_unit_price = None
      if buy_sum == sell_sum:
        PnL_precentage = 0
      else:
        PnL_precentage = ((sell_sum - buy_sum)/buy_sum) * 100
      
    Units_avilable = buy_quant-sell_quant
    current_asset_value = float(Units_avilable) * float(current_price[i])
    result_dict[i] = [Units_avilable,current_price[i],avg_unit_price,current_asset_value,PnL_precentage]  

  result_df = pd.DataFrame(result_dict,index = ['No. Units Avilable','Current Price','Avg Unit Price','Current Asset Value','P / L precentage'])
  result_df = result_df.transpose()
  col_list = list(result_df.columns)
  for i in col_list:
      result_df[i] = result_df[i].astype('float64')
    
  coin_col = list(result_df.index)
  result_df['Asset'] = coin_col
  result_df.sort_values(by = 'Current Asset Value',ascending=False,inplace = True)

  #Chart values
  coin = list(result_df['Asset'])
  chart_values = list(result_df['Current Asset Value'])

# Re arrange the dataframe column 
  df_col = ['Asset','No. Units Avilable','Current Price','Avg Unit Price','Current Asset Value','P / L precentage']
  result_df = result_df[df_col]
  result_df = result_df.round(3)
  table_data = result_df.to_dict('split')

  return coin,chart_values,table_data 

# Check if the file loaded if of correct format
def allowed_files(filename):
    filename = str(filename)
    allowed_ext = ['CSV']
    if "." in (filename):
        ext = filename.rsplit(".",1)[1]
        if ext.upper() in allowed_ext:
            return True
    else:
        return False 