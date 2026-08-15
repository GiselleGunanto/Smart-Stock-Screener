import os
import datetime as dt
import pandas as pd
import yfinance as yf
import requests
from io import StringIO

os.makedirs('stock_data', exist_ok=True)

wiki_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
response = requests.get(wiki_url, headers=headers)

tables = pd.read_html(StringIO(response.text))
tickers = tables[0]['Symbol'].tolist()
tickers = [t.replace('.', '-') for t in tickers]

start = dt.datetime.now() - dt.timedelta(days=365)
end = dt.datetime.now()

sp500_df = yf.download('^GSPC', start=start, end=end, progress=False)

if sp500_df.empty:
    raise ValueError("Failed to fetch S&P 500 data from Yahoo Finance.")

sp500_df['Pct Change'] = sp500_df['Close'].pct_change()

sp500_return = (sp500_df['Pct Change'] + 1).cumprod().iloc[-1]
if isinstance(sp500_return, pd.Series):
    sp500_return = sp500_return.item()

return_list = []
tested_tickers = []

print("Downloading stock data...")
for ticker in tickers:
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        if df.empty:
            continue
            
        df.to_csv(f'stock_data/{ticker}.csv')
        df['Pct Change'] = df['Close'].pct_change()
        stock_return = (df['Pct Change'] + 1).cumprod().iloc[-1]
        if isinstance(stock_return, pd.Series):
            stock_return = stock_return.item()

        returns_compared = round((stock_return / sp500_return), 2)
        return_list.append(returns_compared)
        tested_tickers.append(ticker)
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")

best_performers = pd.DataFrame(list(zip(tested_tickers, return_list)), columns=['Ticker', 'Returns Compared'])
best_performers['Score'] = best_performers['Returns Compared'].rank(pct=True) * 100
best_performers = best_performers[best_performers['Score'] >= best_performers['Score'].quantile(0.7)]

final_list = []

print("Analyzing stock criteria...")
for ticker in best_performers['Ticker']:
    try: 
        df = pd.read_csv(f'stock_data/{ticker}.csv', index_col=0, header=[0, 1])
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df['SMA_150'] = round(df['Close'].rolling(window=150).mean(), 2)
        df['SMA_200'] = round(df['Close'].rolling(window=200).mean(), 2)
        
        latest_price = float(df['Close'].iloc[-1])
        
        stock_info = yf.Ticker(ticker).info
        pe_ratio = stock_info.get('trailingPE', 999)
        peg_ratio = stock_info.get('pegRatio', 999)
        
        moving_average_150 = float(df['SMA_150'].iloc[-1])
        moving_average_200 = float(df['SMA_200'].iloc[-1])
        
        low_52week = round(float(df['Low'].tail(260).min()), 2)
        high_52week = round(float(df['High'].tail(260).max()), 2)
        score = round(best_performers[best_performers['Ticker'] == ticker]['Score'].tolist()[0])

        condition1 = latest_price > moving_average_150 > moving_average_200
        condition2 = latest_price >= (1.3 * low_52week)
        condition3 = latest_price >= (0.75 * high_52week)
        condition4 = pe_ratio < 40
        condition5 = peg_ratio < 2

        if condition1 and condition2 and condition3 and condition4 and condition5:
            final_list.append({
                'Ticker': ticker,
                'Latest_Price': latest_price,
                'Score': score,
                'PE_Ratio': pe_ratio,
                'PEG_Ratio': peg_ratio,
                'SMA_150': moving_average_150,
                'SMA_200': moving_average_200,
                '52_Week_Low': low_52week,
                '52_Week_High': high_52week
            })
            
    except Exception as e:
        print(f"Error screening {ticker}: {e}")


final_df = pd.DataFrame(final_list)

if not final_df.empty:
    final_df = final_df.sort_values(by='Score', ascending=False)
    pd.set_option('display.max_columns', 10)
    print("\n--- RESULTS ---")
    print(final_df)
    final_df.to_csv('final.csv', index=False)
else:
    print("\nExecution complete. No stocks in this sample batch met all conditions.")