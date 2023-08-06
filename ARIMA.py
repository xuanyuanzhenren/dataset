import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
import json
from statsmodels.tsa.stattools import adfuller
import os



def process_data(path):
    f=open(path+'requests','r',encoding='utf-8')
    data=f.readlines()
    data1=[]
    for line in data:
        # 解析 JSON 行
        obj = json.loads(line)

        # 提取 metaKey 和 startTime 字段
        meta_key = obj['metaKey']
        start_time = obj['startTime']
        data1.append([meta_key,start_time])

    df = pd.DataFrame(data1, columns=['metaKey', 'startTime'])
    # 将startTime转换为时间序列（单位秒）
    df['startTime'] = pd.to_datetime(df['startTime'], unit='ms')
    df['startTime'] = df['startTime'].dt.floor('S')
    
    # 按metaKey和startTime分组，计算每秒的请求数
    grouped = df.groupby(['metaKey', 'startTime']).size().reset_index(name='count')
    
    # 对每个metaKey的数据进行处理
    for name, group in grouped.groupby('metaKey'):
        # 创建一个时间序列，范围从最小的startTime到最大的startTime，频率为每秒
        full_index = pd.date_range(start=group['startTime'].min(), end=group['startTime'].max(), freq='S')
        
        # 使用新的时间序列填充原始数据，对于缺失的部分，将count设置为0
        group.set_index('startTime', inplace=True)
        group = group.reindex(full_index, fill_value=0)
        group.reset_index(inplace=True)
        group.rename(columns={'index': 'startTime'}, inplace=True)
        
        # 从DataFrame中删除metaKey列
        group.drop(['metaKey'], axis=1, inplace=True)
        
        # 将处理后的数据保存为CSV文件
        group.to_csv(path+"processed_data/"+f"{name}.csv", index=False)
    
    return grouped


def determine_d(timeseries):
    # 定义最大的p值，最小的p值和对应的d值
    max_p_value = 1.0
    best_d = 0

    # 对0-100范围内的d值进行循环测试
    for d in range(100):
        temp_series = timeseries.diff(d).dropna()
        p_value = adfuller(temp_series)[1]
        if p_value < max_p_value:
            max_p_value = p_value
            best_d = d
        if p_value < 0.05:
            break

    print(f"Best d value: {best_d}")
    return best_d

def determine_pq(path):
    # 绘制ACF和PACF图，以确定ARIMA模型的p和q参数
    # 从CSV文件中读取数据
    files=os.listdir(path+"processed_data")
    for file in files:
        file_name=file.split(".")[0]
        data = pd.read_csv(path+"processed_data/"+file, header=0)
        plot_acf(data['count'],lags=200)
        plt.savefig(path+"acf/"+f"{file_name}_acf.pdf")
        plt.close()
        plot_pacf(data['count'],lags=400)
        plt.savefig(path+"pacf/"+f"{file_name}_pacf.pdf")
        plt.close()


    # 绘制ACF和PACF图
    plot_acf(data['count'])
    plot_pacf(data['count'])
    plt.show()


# 使用函数
# 假设df是原始数据
# df = pd.DataFrame(data, columns=['metaKey', 'startTime'])
def main():
    paths=['./dataSet_1/','./dataSet_2/','./dataSet_3/']
    # paths=['./dataSet_1/']
    for path in paths:
        files=os.listdir(path+"processed_data")
        for file in files:
            file_name=file.split(".")[0]
            data = pd.read_csv(path+"processed_data/"+file, header=0)
            best_d=determine_d(data["count"])
            with open(path+"best_d.txt",'a+',encoding='utf-8') as f:
                f.write(file_name+"'s best_d: "+str(best_d)+'\n')

            
                

    
main()