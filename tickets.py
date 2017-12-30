'''
Copyright (C) 王适存 Rights Reserved
时间 2017/12/30
这是一个爬取12306信息的爬虫软件
example:
     python tickets.py 上海 成都 2018-1-23
     爬取上海到成都2018-1-23号的车票信息
注释信息：
     stationurl是12306一个用js格式封装的车站名称与车站代码之间的对应关系
     url是车票信息地址，用json格式封装了信息
总结：
    这个爬虫本身思想很简单，但可能是12306官方为了不让被人轻易
    爬取它的信息，增设了很多难度，collection中的正则表达式是根据实际
    实践总结的方法，因为12306官方不断改变版本，不具有时效性
'''
import requests
import re
import argparse
from prettytable import PrettyTable
def collection(url,reversdic_station):                  #收集车票信息
    res = requests.get(url, verify=False)
    results = res.json()['data']['result']
    trains=[]
    for line in results:
        r1 = re.search('预订\|[0-9](.*)', line)
        if r1:
            newlist = list(str(r1.group(1)))
        else:
            continue
        del newlist[0]
        dostr = ''.join(newlist)
        msg1 = re.findall('\|([0-9A-Z:]+)', dostr)
        usemsg1 = [msg1[0], msg1[3], msg1[4], msg1[5], msg1[6], msg1[7]]
        usemsg1[1] = reversdic_station[usemsg1[1]]
        usemsg1[2] = reversdic_station[usemsg1[2]]
        msg2 = re.search('\|[10]\|0(.*?)[0-9A-Z]{4,6}', dostr).group(1)
        msg3 = re.findall('\|([^\|]*)', msg2)
        usemsg2 = [msg3[3], msg3[6], msg3[8], msg3[9], msg3[10], msg3[11]]
        for i in range(len(usemsg2)):
            if usemsg2[i]=='':
                usemsg2[i]='--'
        usemsg1.extend(usemsg2)
        msg=usemsg1
        trains.append(msg)
    return trains
def pretty_print(trains):    #打印
    header = '车次 始发站 目的站 出发时间 到达时间 历时 软卧 无座 硬卧 硬座 二等座 一等座'.split()
    pt=PrettyTable()
    pt._set_field_names(header)
    for train in trains:
        pt.add_row(train)
    print(pt)
def value_key(dic_stations):   #将字典的键值对应关系转换，即由原先的键对应值转换为值对应键
    newdic_stations={}
    for key,value in dic_stations.items():
        newdic_stations[value]=key
    return newdic_stations
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('fromStation',type=str)
    parser.add_argument('toStation',type=str)
    parser.add_argument('trainDate',type=str)
    args=parser.parse_args()
    letterfrom_station=args.fromStation
    letterto_station=args.toStation
    train_date=args.trainDate
    stationUrl = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9039'
    res = requests.get(stationUrl, verify=False)
    stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', res.text)
    dic_stations=dict(stations)
    reversdic_stations=value_key(dic_stations)
    from_station=dic_stations[letterfrom_station]
    to_station=dic_stations[letterto_station]
    url='https://kyfw.12306.cn/otn/leftTicket/queryO?' \
        'leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&' \
        'leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(train_date,from_station,to_station)
    trains=collection(url,reversdic_stations)
    pretty_print(trains)
if __name__=='__main__':
    main()
