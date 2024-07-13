import pandas as pd

def read_and_process_csv(file_path):
    # 讀取CSV檔案
    df = pd.read_csv(file_path)
    # 清理列名中的空白字元
    df.columns = df.columns.str.strip()

    # 處理日期與時間
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df = df.drop(columns=['Date', 'Time'])

    # 將Last這個column改名稱為Close
    df = df.rename(columns={'Last': 'Close'})

    # 設置Datetime為索引
    df = df.set_index('Datetime')

    return df