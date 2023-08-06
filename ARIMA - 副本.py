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

def get_p_q(grouped):

    for name, group in grouped:
        print(f"Processing {name}")
        
        # 将时间转换为每秒，并计算每秒的请求数
        group['second'] = group['startTime'].dt.floor('S')
        group = group.groupby('second').size().reset_index(name='request_count')
        
        # 画出ACF和PACF图以确定p和q参数
        plot_acf(group['request_count'])
        plot_pacf(group['request_count'])
        plt.show()
        
        # 根据ACF和PACF图选择合适的p和q参数，d通常设为1
        p = 1  # 替换为你从图中观察到的值
        q = 1  # 替换为你从图中观察到的值
        d = 1  # 通常设为1
        
        # 拟合ARIMA模型
        model = ARIMA(group['request_count'], order=(p,d,q))
        model_fit = model.fit(disp=0)
        
        print(model_fit.summary())



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
    plot_acf(df)
    plot_pacf(df)
    plt.show()
    # 从CSV文件中读取数据
    files=os.listdir(path+"processed_data")
    for file in files:
        file_name=file.split(".")[0]
        data = pd.read_csv(path+"processed_data/"+file, header=0)
        plot_acf(data['count'])
        plt.savefig(path+"acf/"+f"{file_name}_acf.pdf")
        plt.close()
        plot_pacf(data['count'])
        plt.savefig(path+"pacf/"+f"{file_name}_acf.pdf")
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

            
                

    
def main3():
    # 数据预处理
    df=0
    processed_df = process_data(df)

    # 对每个metaKey的数据进行处理
    grouped = processed_df.groupby('metaKey')
    for name,group in grouped:
        # 进行单位根检验
        # print("Performing stationarity test:")
        # test_stationarity(group['count'])
        
        # 根据单位根检验的结果确定d值（如果p值小于0.05，d=0，否则d=1）
        d = determine_d(group['count'])
        with open('./dataSet_2/d.txt','a+',encoding='utf-8') as f:
            f.write(f"{name}'s determined d={d}\n") ;
        # print(f"{name}'s determined d={d}")

def main2():
    grouped=0
    for name, group in grouped:
        print(f"Processing {name}")
        
        # 进行单位根检验
        print("Performing stationarity test:")
        test_stationarity(group['count'])
        
        # 根据单位根检验的结果确定d值（如果p值小于0.05，d=0，否则d=1）
        d = 0 if adfuller(group['count'])[1] < 0.05 else 1
        print(f"determined d={d}")
        
        # 确定p和q值
        print("Determining p and q:")
        determine_pq(group['count'])
    
main()