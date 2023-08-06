import json
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import matplotlib.dates as mdates

def main():
    # 假设 data 是一个包含所有 JSON 行的列表
    # data = [
        # '{"metaKey": "nodes1", "startTime": 1685980824304, "durationsInMs": 2542, "statusCode": 200}',
        # '{"metaKey": "nodes1", "startTime": 1685980854304, "durationsInMs": 2651, "statusCode": 200}',
        # 更多数据...
    # ]
    # 创建一个 defaultdict，键是 metaKey，值是 (startTime, count) 列表
    request_counts = defaultdict(list)
    datasets=["./dataSet_1/","./dataSet_2/","./dataSet_3/"]
    for dataset in datasets:
        f=open(dataset+"requests",'r',encoding='utf-8')
        data=f.readlines()
        for line in data:
            # 解析 JSON 行
            obj = json.loads(line)

            # 提取 metaKey 和 startTime 字段
            meta_key = obj['metaKey']
            start_time = obj['startTime']

            # 如果这个 metaKey 还没有任何请求，添加一个新的 (startTime, count) 对
            if not request_counts[meta_key] or request_counts[meta_key][-1][0] != start_time:
                request_counts[meta_key].append([start_time, 1])
            else:
                # 否则，增加最后一个 (startTime, count) 对的 count
                request_counts[meta_key][-1][1] += 1

        # 为每个 metaKey 绘制一个折线图
        for meta_key, counts in request_counts.items():
            times, counts = zip(*counts)

            # 将 Unix 时间戳转换为 pandas DateTime 对象
            times = pd.to_datetime(times, unit='ms')

            plt.plot(times, counts, label=meta_key)
        # 在上述代码后面添加下面的内容

        # 设置 x 轴的日期格式
        ax = plt.gca()  # 获取当前的轴
        formatter = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")  # 设置日期格式，包括年、月、日、小时、分钟和秒
        ax.xaxis.set_major_formatter(formatter)

        # 自动旋转 x 轴的日期标签以避免重叠
        plt.gcf().autofmt_xdate()
        plt.legend()
        plt.savefig(dataset+"request.pdf",dpi=3000)
        # plt.show()   

main()


# # 在上述代码后面添加下面的内容

# # 设置 x 轴的日期格式
# ax = plt.gca()  # 获取当前的轴
# formatter = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")  # 设置日期格式，包括年、月、日、小时、分钟和秒
# ax.xaxis.set_major_formatter(formatter)

# # 自动旋转 x 轴的日期标签以避免重叠
# plt.gcf().autofmt_xdate()

# plt.legend()
# plt.show()