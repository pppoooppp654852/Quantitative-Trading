import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from packages import read_and_process_csv
import numpy as np

# 讀取CSV檔案
df = read_and_process_csv('data/BTCUSDT_80000t.csv')

# 標記pivot points的函數
def mark_pivot_points(df, n):
    df['PP'] = 'N/A'
    last_low_index = df.index[0]
    last_high_index = df.index[0]
    last_low_value = float('inf')
    last_high_value = float('-inf')
    step = n // 2
    
    prev_mark = 'N/A'

    for i in range(0, len(df), step):
        start = max(i - n // 2, 0)
        end = min(i + n // 2 + 1, len(df))
        local_high_index = df[start:end]['High'].idxmax()
        local_low_index = df[start:end]['Low'].idxmin()
        local_high_value = df.loc[local_high_index, 'High']
        local_low_value = df.loc[local_low_index, 'Low']
        
        if prev_mark == 'HH' or prev_mark == 'LH' or prev_mark == 'N/A':
            if local_low_value < last_low_value:
                df.at[local_low_index, 'PP'] = 'LL'
                prev_mark = 'LL'
            else:
                df.at[local_low_index, 'PP'] = 'HL'
                prev_mark = 'HL'
                
            # if local_high_value > last_high_value:
            #     df.at[last_high_index, 'PP'] = 'N/A'
            #     df.at[local_high_index, 'PP'] = 'HH'
                
            last_low_index = local_low_index
            last_low_value = local_low_value
            # print('prev_mark:', prev_mark)
        elif prev_mark == 'LL' or prev_mark == 'HL' or prev_mark == 'N/A':
            if local_high_value > last_high_value:
                df.at[local_high_index, 'PP'] = 'HH'
                prev_mark = 'HH'
            else:
                df.at[local_high_index, 'PP'] = 'LH'
                prev_mark = 'LH'
            last_high_index = local_high_index
            last_high_value = local_high_value
            # print('prev_mark:', prev_mark)

    # 創建標記數據
    mark_offset = 200
    ll_points = np.where(df['PP'] == 'LL', df['Low'] - mark_offset, np.nan)
    hl_points = np.where(df['PP'] == 'HL', df['Low'] - mark_offset, np.nan)
    hh_points = np.where(df['PP'] == 'HH', df['High'] + mark_offset, np.nan)
    lh_points = np.where(df['PP'] == 'LH', df['High'] + mark_offset, np.nan)

    return df, ll_points, hl_points, hh_points, lh_points

n = 20
df, ll_points, hl_points, hh_points, lh_points = mark_pivot_points(df, n)

# Set display options to show all rows and columns
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Now print the first 100 rows
print(df.head(100))

# 設置初始顯示的區間
window = 300
start = 0
end = window

my_style = mpf.make_mpf_style(gridstyle='None')

fig = mpf.figure(style=my_style)
ax1 = fig.add_axes([0.05, 0.15, 0.95, 0.8])
ax2 = fig.add_axes([0.1, 0.05, 0.9, 0.05])

ax1.grid(False)


# 初始繪製
def plot_candlestick(start, end):
    ax1.clear()
    apds = [
        mpf.make_addplot(ll_points[start:end], ax=ax1, type='scatter', markersize=100, marker='^', color='red'),
        mpf.make_addplot(hl_points[start:end], ax=ax1, type='scatter', markersize=100, marker='^', color='red'),
        mpf.make_addplot(hh_points[start:end], ax=ax1, type='scatter', markersize=100, marker='v', color='green'),
        mpf.make_addplot(lh_points[start:end], ax=ax1, type='scatter', markersize=100, marker='v', color='green'),
    ]
    mpf.plot(df.iloc[start:end], ax=ax1, type='candle', volume=False, addplot=apds)
    fig.canvas.draw_idle()

plot_candlestick(start, end)


# 添加滑動條
slider = Slider(ax2, 'Scroll', 0, len(df) - window, valinit=start, valstep=1)

def update(val):
    start = int(slider.val)
    end = start + window
    plot_candlestick(start, end)

slider.on_changed(update)

# 最大化視窗
fig.set_size_inches(18, 10)
plt.get_current_fig_manager().window.wm_geometry("1920x1080+0+0")

mpf.show()
