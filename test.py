

def main():
    f1=open("./dataSet_1/requests",'w',encoding='utf-8')
    with open("./dataSet_1/requests.txt",'r',encoding='utf-8') as f:
        lines=f.readlines()
        lines=lines[:1000]
        f1.writelines(lines)
    f1.close()
main()