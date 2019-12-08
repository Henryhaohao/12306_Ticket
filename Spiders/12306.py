# !/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Henry'


'''
12306-余票查询+订票+退票
20190416登录更新:
    必须cookie加上RAIL_DEVICEID(https://kyfw.12306.cn/otn/HttpZF/logdevice这个接口返回的)
    要不然会登录失败,返回"网络可能存在问题，请您重试一下！",会跳转到https://www.12306.cn/mormhweb/logFiles/error.html
    
20190721更新:
    选择乘客信息查询余票时多提交了一个allEncStr字段
'''


import requests, re, time, ssl, urllib
from urllib import parse
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import urllib3

urllib3.disable_warnings() #不显示警告信息
ssl._create_default_https_context = ssl._create_unverified_context
req = requests.Session()

# 获取RAIL_DEVICEID写在登录之前get_rail_deviceid()函数
# req.cookies['RAIL_DEVICEID'] = 'ng8GWpVBAs1dnOxtsAEnQ1EyfbEuCIGetci8OLRrXAtY_grSokW5WZb10aDdNS_Je4KbKlgf3fPtO4cZJGCox4ORGXGZ8Fhcq6TDWW1iuLlaU2kLccvL22V_HBd49idoCqL0dJEbfl3Plhhno73VZqQY5aKeAHHJ'


class Leftquery(object):
    '''余票查询'''

    def __init__(self):
        self.station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        self.headers = {
            'Host': 'kyfw.12306.cn',
            'If-Modified-Since': '0',
            'Pragma': 'no-cache',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

    def station_name(self, station):
        '''获取车站简拼'''
        html = requests.get(self.station_url, verify=False).text
        result = html.split('@')[1:]
        dict = {}
        for i in result:
            key = str(i.split('|')[1])
            value = str(i.split('|')[2])
            dict[key] = value
        return dict[station]

    def query(self, from_station, to_station, date):
        '''余票查询'''
        fromstation = self.station_name(from_station)
        tostation = self.station_name(to_station)
        url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
            date, fromstation, tostation)
        # 学生票查询: url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=0X00'.format(date, fromstation, tostation)
        try:
            html = requests.get(url, headers=self.headers, verify=False).json()
            result = html['data']['result']
            if result == []:
                print('很抱歉,没有查到符合当前条件的列车!')
                exit()
            else:
                print(date + from_station + '-' + to_station + '查询成功!')
                # 打印出所有车次信息
                num = 1  # 用于给车次编号,方便选择要购买的车次
                for i in result:
                    info = i.split('|')
                    if info[0] != '' and info[0] != 'null':
                        print(str(num) + '.' + info[3] + '车次还有余票:')
                        print('出发时间:' + info[8] + ' 到达时间:' + info[9] + ' 历时多久:' + info[10] + ' ', end='')
                        seat = {21: '高级软卧', 23: '软卧', 26: '无座', 28: '硬卧', 29: '硬座', 30: '二等座', 31: '一等座', 32: '商务座',
                                33: '动卧'}
                        from_station_no = info[16]
                        to_station_no = info[17]
                        for j in seat.keys():
                            if info[j] != '无' and info[j] != '':
                                if info[j] == '有':
                                    print(seat[j] + ':有票 ', end='')
                                else:
                                    print(seat[j] + ':有' + info[j] + '张票 ', end='')
                        print('\n')
                    elif info[1] == '预订':
                        print(str(num) + '.' + info[3] + '车次暂时没有余票')
                    elif info[1] == '列车停运':
                        print(str(num) + '.' + info[3] + '车次列车停运')
                    elif info[1] == '23:00-06:00系统维护时间':
                        print(str(num) + '.' + info[3] + '23:00-06:00系统维护时间')
                    else:
                        print(str(num) + '.' + info[3] + '车次列车运行图调整,暂停发售')
                    num += 1
            return result
        except:
            print('查询信息有误!请重新输入!')
            exit()


class Login(object):
    '''登录模块'''

    def __init__(self):
        self.username = username
        self.password = password
        self.url_pic = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.15905700266966694'
        self.url_check = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        self.url_login = 'https://kyfw.12306.cn/passport/web/login'
        # self.url_rail_deviceid = 'https://kyfw.12306.cn/otn/HttpZF/logdevice?algID=LViaqcvRbo&hashCode=RONh1-EomRApoVf1W9XrJYsBeCduvqTrQis5xPyHS_o&FMQw=1&q4f3=zh-CN&VySQ=FGExA0W53bSl7MR7lAZtO9-whgi60qgC&VPIf=1&custID=133&VEek=unknown&dzuS=29.0%20r0&yD16=0&EOQP=f57fa883099df9e46e7ee35d22644d2b&lEnu=3232235621&jp76=7047dfdd1d9629c1fb64ef50f95be7ab&hAqN=Win32&platform=WEB&ks0Q=6f0fab7b40ee4a476b4b3ade06fe9065&TeRS=1080x1920&tOHY=24xx1080x1920&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&0aew=Mozilla/5.0%20(Windows%20NT%206.1;%20WOW64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/63.0.3239.132%20Safari/537.36&E3gR=fd7a8adb89dd5bf3a55038ad1adc5d35&timestamp='
        self.headers = {
            # 'Accept': 'application/json, text/javascript, */*; q=0.01',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'kyfw.12306.cn',
            # 'Referer': 'https://kyfw.12306.cn/otn/login/init',
            'Referer': 'https://kyfw.12306.cn/otn/resources/login.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }

    def get_rail_deviceid(self):
        '''获取rail_deviceid'''
        global req
        html = requests.get('https://kyfw.12306.cn/otn/HttpZF/GetJS', headers=self.headers).text
        algID = re.search(r'algID\\x3d(.*?)\\x', html).group(1)
        # print('algID:' + algID)
        url_rail_deviceid = 'https://kyfw.12306.cn/otn/HttpZF/logdevice?algID={}&hashCode=lcDbed2Mzz_ujxMm4wqJJGdtpwewNfaD9ls9fevDi7s&FMQw=1&q4f3=zh-CN&VySQ=FGHsTPLNUtnxKqG7cFTyIU0TP2MHNCET&VPIf=1&custID=133&VEek=unknown&dzuS=0&yD16=0&EOQP=4902a61a235fbb59700072139347967d&jp76=22c403d29cd09c89fdb5ff4f63770421&hAqN=Win32&platform=WEB&ks0Q=d22ca0b81584fbea62237b14bd04c866&TeRS=1112x2048&tOHY=24xx1152x2048&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&0aew=Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/78.0.3904.108%20Safari/537.36&E3gR=193e1e48dda80e6170a08ad4ab99686d&timestamp='.format(
            algID)
        html_rail_deviceid = req.get(url_rail_deviceid+ str(int(time.time()*1000)),headers=self.headers).text
        rail_deviceid = re.search(r'"dfp":"(.*?)"', html_rail_deviceid).group(1)
        req.cookies['RAIL_DEVICEID'] = rail_deviceid

    def showimg(self):
        '''显示验证码图片'''
        global req
        html_pic = req.get(self.url_pic, headers=self.headers).content
        open('pic.jpg', 'wb').write(html_pic)
        img = mpimg.imread('pic.jpg')
        plt.imshow(img)
        plt.axis('off')
        plt.show()

    def captcha(self, answer_num):
        '''填写验证码'''
        answer_sp = answer_num.split(',')
        answer_list = []
        an = {'1': (31, 35), '2': (116, 46), '3': (191, 24), '4': (243, 50), '5': (22, 114), '6': (117, 94),
              '7': (167, 120), '8': (251, 105)}
        for i in answer_sp:
            for j in an.keys():
                if i == j:
                    answer_list.append(an[j][0])
                    answer_list.append(',')
                    answer_list.append(an[j][1])
                    answer_list.append(',')
        s = ''
        for i in answer_list:
            s += str(i)
        answer = s[:-1]
        # 验证验证码
        form_check = {
            'answer': answer,
            'login_site': 'E',
            'rand': 'sjrand',
            '_': str(int(time.time() * 1000))
        }
        global req
        html_check = req.get(self.url_check, params=form_check, headers=self.headers).json()
        print(html_check)
        if html_check['result_code'] == '4':
            print('验证码校验成功!')
        else:
            print('验证码校验失败!')
            exit()

    def login(self, answer_num):
        '''登录账号'''
        answer_sp = answer_num.split(',')
        answer_list = []
        an = {'1': (31, 35), '2': (116, 46), '3': (191, 24), '4': (243, 50), '5': (22, 114), '6': (117, 94),
              '7': (167, 120), '8': (251, 105)}
        for i in answer_sp:
            for j in an.keys():
                if i == j:
                    answer_list.append(an[j][0])
                    answer_list.append(',')
                    answer_list.append(an[j][1])
                    answer_list.append(',')
        s = ''
        for i in answer_list:
            s += str(i)
        answer = s[:-1]
        form_login = {
            'username': self.username,
            'password': self.password,
            'appid': 'otn',
            'answer': answer
        }
        print(form_login)
        global req
        # self.headers['Content-Length'] = str(len(urllib.parse.urlencode(form_login)))
        # 20190416更新-必须cookie加上RAIL_DEVICEID(https://kyfw.12306.cn/otn/HttpZF/logdevice这个借口返回的,写成定值即可,2030年过期)
        # 要不然会登录失败,返回"网络可能存在问题，请您重试一下！",会跳转到https://www.12306.cn/mormhweb/logFiles/error.html
        # req.cookies['RAIL_DEVICEID'] = 'g9qXFFIFQ4jPKuxX6YTC38yc0xdYE2QfbPKdtS8HpYXgY9yKKaQGR2eOG-Kx67d6Hp-keCyhUqjc7pokitcskwj5X9i72soSkvlc4qFQ2hf-abUpuwvcHjww4n_kxYXe9tFbCAV_1VFtCQS64hAyI0ycCQgLbQDW'
        html_login = req.post(self.url_login, data=form_login, headers=self.headers).json()
        print(html_login)
        # print(html_login['headers']['Content-Length'])
        if html_login['result_code'] == 0:
            print('恭喜您,登录成功!')
        else:
            print('账号密码错误,登录失败!')
            exit()


class Order(object):
    '''提交订单'''

    def __init__(self):
        self.url_uam = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        self.url_uamclient = 'https://kyfw.12306.cn/otn/uamauthclient'
        self.url_checkUser = 'https://kyfw.12306.cn/otn/login/checkUser'
        self.url_order = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        self.url_token = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        self.url_pass = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        self.url_confirm = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        self.url_checkorder = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        self.url_count = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        self.head_1 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        self.head_2 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }

    def auth(self):
        '''验证uamtk和uamauthclient'''
        # 验证uamtk
        form = {
            'appid': 'otn',
            # '_json_att':''
        }
        global req
        html_uam = req.post(self.url_uam, data=form, headers=self.head_1).json()
        print(html_uam)
        if html_uam['result_code'] == 0:
            print('恭喜您,uam验证成功!')
        else:
            print('uam验证失败!')
            exit()
        # 验证uamauthclient
        tk = html_uam['newapptk']

        form = {
            'tk': tk,
            # '_json_att':''
        }
        html_uamclient = req.post(self.url_uamclient, data=form, headers=self.head_1).json()
        print(html_uamclient)
        if html_uamclient['result_code'] == 0:
            print('恭喜您,uamclient验证成功!')
        else:
            print('uamclient验证失败!')
            exit()

    def order(self, result, train_number, from_station, to_station, date):
        '''提交订单'''
        # 用户选择要购买的车次的序号
        secretStr = parse.unquote(result[int(train_number) - 1].split('|')[0])
        back_train_date = time.strftime("%Y-%m-%d", time.localtime())
        form = {
            'secretStr': secretStr,  # 'secretStr':就是余票查询中你选的那班车次的result的那一大串余票信息的|前面的字符串再url解码
            'train_date': date,  # 出发日期(2018-04-08)
            'back_train_date': back_train_date,  # 查询日期
            'tour_flag': 'dc',  # 固定的
            'purpose_codes': 'ADULT',  # 成人票
            'query_from_station_name': from_station,  # 出发地
            'query_to_station_name': to_station,  # 目的地
            'undefined': ''  # 固定的
        }
        global req
        html_order = req.post(self.url_order, data=form, headers=self.head_1).json()
        print(html_order)
        if html_order['status'] == True:
            print('恭喜您,提交订单成功!')
        else:
            print('提交订单失败!')
            exit()

    def price(self):
        '''打印票价信息'''
        form = {
            '_json_att': ''
        }
        global req
        html_token = req.post(self.url_token, data=form, headers=self.head_1).text
        token = re.findall(r"var globalRepeatSubmitToken = '(.*?)';", html_token)[0]
        leftTicket = re.findall(r"'leftTicketStr':'(.*?)',", html_token)[0]
        key_check_isChange = re.findall(r"'key_check_isChange':'(.*?)',", html_token)[0]
        train_no = re.findall(r"'train_no':'(.*?)',", html_token)[0]
        stationTrainCode = re.findall(r"'station_train_code':'(.*?)',", html_token)[0]
        fromStationTelecode = re.findall(r"'from_station_telecode':'(.*?)',", html_token)[0]
        toStationTelecode = re.findall(r"'to_station_telecode':'(.*?)',", html_token)[0]
        date_temp = re.findall(r"'to_station_no':'.*?','train_date':'(.*?)',", html_token)[0]
        timeArray = time.strptime(date_temp, "%Y%m%d")
        timeStamp = int(time.mktime(timeArray))
        time_local = time.localtime(timeStamp)
        train_date_temp = time.strftime("%a %b %d %Y %H:%M:%S", time_local)
        train_date = train_date_temp + ' GMT+0800 (中国标准时间)'
        train_location = re.findall(r"tour_flag':'.*?','train_location':'(.*?)'", html_token)[0]
        purpose_codes = re.findall(r"'purpose_codes':'(.*?)',", html_token)[0]
        print('token值:' + token)
        print('leftTicket值:' + leftTicket)
        print('key_check_isChange值:' + key_check_isChange)
        print('train_no值:' + train_no)
        print('stationTrainCode值:' + stationTrainCode)
        print('fromStationTelecode值:' + fromStationTelecode)
        print('toStationTelecode值:' + toStationTelecode)
        print('train_date值:' + train_date)
        print('train_location值:' + train_location)
        print('purpose_codes值:' + purpose_codes)
        price_list = re.findall(r"'leftDetails':(.*?),'leftTicketStr", html_token)[0]
        # price = price_list[1:-1].replace('\'', '').split(',')
        print('票价:')
        for i in eval(price_list):
            # p = i.encode('latin-1').decode('unicode_escape')
            # print(i.replace('一等卧','软卧').replace('二等卧','硬卧') + ' | ', end='')
            print(i + ' | ', end='')
        return train_date, train_no, stationTrainCode, fromStationTelecode, toStationTelecode, leftTicket, purpose_codes, train_location, token, key_check_isChange

    def passengers(self, token):
        '''打印乘客信息'''
        # 确认乘客信息
        form = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_pass = req.post(self.url_pass, data=form, headers=self.head_1).json()
        passengers = html_pass['data']['normal_passengers']
        print('\n')
        print('乘客信息列表:')
        for i in passengers:
            print(str(int(i['index_id']) + 1) + '号:' + i['passenger_name'] + ' | ', end='')
        print('\n')
        return passengers

    def chooseseat(self, passengers, passengers_name, choose_seat, token):
        '''选择乘客和座位'''
        seat_dict = {'无座': '1', '硬座': '1', '硬卧': '3', '二等卧': 'J','软卧': '4','一等卧': 'I', '高级软卧': '6', '动卧': 'F', '二等座': 'O', '一等座': 'M',
                     '商务座': '9'}
        choose_type = seat_dict[choose_seat]
        pass_num = len(passengers_name.split(','))  # 购买的乘客数
        pass_list = passengers_name.split(',')
        pass_dict = []
        for i in pass_list:
            info = passengers[int(i) - 1]
            pass_name = info['passenger_name']  # 名字
            pass_id = info['passenger_id_no']  # 身份证号
            pass_phone = info['mobile_no']  # 手机号码
            pass_type = info['passenger_type']  # 证件类型
            allEncStr = info['allEncStr']  # 加密字符串
            dict = {
                'choose_type': choose_type,
                'pass_name': pass_name,
                'pass_id': pass_id,
                'pass_phone': pass_phone,
                'pass_type': pass_type,
                'allEncStr': allEncStr
            }
            pass_dict.append(dict)

        passengerTicketStr = ''
        for i in pass_dict:
            TicketStr = i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                'pass_id'] + ',' + i['pass_phone'] + ',N,' + i['allEncStr']
            passengerTicketStr += TicketStr + '_'

        passengerTicketStr = passengerTicketStr[:-1]
        print(passengerTicketStr)

        num = 0
        passengrStr_list = []
        for i in pass_dict:
            if pass_num == 1:
                passengerStr = i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ',1_'
                passengrStr_list.append(passengerStr)
            elif num == 0:
                passengerStr = i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ','
                passengrStr_list.append(passengerStr)
            elif num == pass_num - 1:
                passengerStr = '1_' + i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ',1_'
                passengrStr_list.append(passengerStr)
            else:
                passengerStr = '1_' + i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ','
                passengrStr_list.append(passengerStr)
            num += 1

        oldpassengerStr = ''.join(passengrStr_list)
        print(oldpassengerStr)
        form = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldpassengerStr,
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_checkorder = req.post(self.url_checkorder, data=form, headers=self.head_2).json()
        print(html_checkorder)
        if html_checkorder['status'] == True:
            print('检查订单信息成功!')
        else:
            print('检查订单信息失败!')
            exit()

        return passengerTicketStr, oldpassengerStr, choose_type

    def leftticket(self, train_date, train_no, stationTrainCode, choose_type, fromStationTelecode, toStationTelecode,
                   leftTicket, purpose_codes, train_location, token):
        '''查看余票数量'''
        form = {
            'train_date': train_date,
            'train_no': train_no,
            'stationTrainCode': stationTrainCode,
            'seatType': choose_type,
            'fromStationTelecode': fromStationTelecode,
            'toStationTelecode': toStationTelecode,
            'leftTicket': leftTicket,
            'purpose_codes': purpose_codes,
            'train_location': train_location,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_count = req.post(self.url_count, data=form, headers=self.head_2).json()
        print(html_count)
        if html_count['status'] == True:
            print('查看余票数量成功!')
            count = html_count['data']['ticket']
            print('此座位类型还有余票' + count + '张~')
        else:
            print('查看余票数量失败!')
            exit()

    def sure(self):
        '''是否确认购票'''
        # 用户是否继续购票:
        i = input('是否确定购票?(Y or N):')
        if i == 'Y' or i == 'y':
            pass
        else:
            exit()

    def confirm(self, passengerTicketStr, oldpassengerStr, key_check_isChange, leftTicket, purpose_codes,
                train_location, token):
        '''最终确认订单'''
        form = {
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldpassengerStr,
            'randCode': '',
            'key_check_isChange': key_check_isChange,
            'choose_seats': '',
            'seatDetailType': '000',
            'leftTicketStr': leftTicket,
            'purpose_codes': purpose_codes,
            'train_location': train_location,
            '_json_att': '',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_confirm = req.post(self.url_confirm, data=form, headers=self.head_2).json()
        print(html_confirm)
        if html_confirm['status'] == True:
            print('确认购票成功!')
        else:
            print('确认购票失败!')
            exit()


class Cancelorder(Login, Order):
    '''取消订单'''

    def __init__(self):
        Login.__init__(self)
        Order.__init__(self)
        self.url_ordeinfo = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete'
        self.url_cancel = 'https://kyfw.12306.cn/otn/queryOrder/cancelNoCompleteMyOrder'
        self.head_cancel = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/queryOrder/initNoComplete',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }

    def orderinfo(self):
        '''查询未完成订单'''
        form = {
            '_json_att': ''
        }
        global req

        html_orderinfo = req.post(self.url_ordeinfo, data=form, headers=self.head_cancel).json()
        if html_orderinfo['status'] == True:
            print('查询未完成订单成功!')
            try:
                order_info = html_orderinfo['data']['orderDBList'][0]
                pass_list = order_info['array_passser_name_page']
                sequence_no = order_info['tickets'][0]['sequence_no']
                train_date = order_info['start_train_date_page']
                from_station = order_info['from_station_name_page'][0]
                to_station = order_info['to_station_name_page'][0]
                print('订单详情:')
                print(train_date, from_station, to_station, pass_list, sequence_no, end='')
                return sequence_no
            except:
                print('抱歉,您没有未完成的订单!')
                exit()
        else:
            print('查询未完成订单失败!')
            exit()

    def confirmcancel(self, sequence_no):
        '''确认取消订单'''
        print('\n')
        i = input('是否确定取消该订单?(Y or N):')
        if i == 'Y' or i == 'y':
            form = {
                'sequence_no': sequence_no,  # 订单号('EF20783324')
                'cancel_flag': 'cancel_order',  # 固定
                '_json_att': ''
            }
            global req
            html_cancel = req.post(self.url_cancel, data=form, headers=self.head_cancel).json()
            print(html_cancel)
            if html_cancel['status'] == True:
                print('取消订单成功!')
            else:
                print('取消订单失败!')
        else:
            print('退出取消订单程序...')
            exit()


class Cancelticket(Login, Order):
    '''退票'''

    def __init__(self):
        Login.__init__(self)
        Order.__init__(self)
        self.url_query = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrder'
        self.url_return = 'https://kyfw.12306.cn/otn/queryOrder/returnTicketAffirm'
        self.url_end = 'https://kyfw.12306.cn/otn/queryOrder/returnTicket'
        self.head_query = {
            'Referer': 'https://kyfw.12306.cn/otn/queryOrder/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }

    def queryorder(self, querytype, startdate, enddate, train_info):
        '''查询历史订单'''
        form = {
            'queryType': querytype,  # 1:按订票日期查询 ; 2:按乘车日期查询
            'queryStartDate': startdate,  # 查询起始日期
            'queryEndDate': enddate,  # 查询最终日期
            'come_from_flag': 'my_order',
            'pageSize': '8',
            'pageIndex': '0',  # 翻页
            'query_where': 'G',
            'sequeue_train_name': train_info,  # 填乘客姓名('xxx')或车次号('K1561')或订单号('EF159626'); 也可以不填('')
        }
        global req
        html_query = req.post(self.url_query, headers=self.head_query, data=form).json()
        if html_query['data']['order_total_number'] == '':
            print('抱歉,没有查到相关订单~')
            exit()
        else:
            print('查询订单成功!一共有' + html_query['data']['order_total_number'] + '个订单:')
            data = html_query['data']['OrderDTODataList']  # 订单信息
            order_num = 1
            for i in data:
                ticket_list = i['tickets']  # 票信息(一个订单里可能有几张票,同时买的)
                print('订单' + str(order_num) + ':')
                ticket_num = 1
                for j in ticket_list:
                    sequence_no = j['sequence_no']  # 订单号 (EF58532938)
                    pass_name = j['passengerDTO']['passenger_name']  # 乘客姓名
                    ticket_status_name = j['ticket_status_name']  # 订单状态(已支付或者已退票(业务流水号:2EF86141313001001085307256))
                    seat_type_name = j['seat_type_name']  # 座位类型 (硬卧)
                    seat_name = j['seat_name']  # 座位号 (16号上铺)
                    price = j['str_ticket_price_page']  # 票价(96.0)
                    train_code = j['stationTrainDTO']['station_train_code']  # 车次号(短:K1561)
                    date = j['start_train_date_page']  # 乘车日期+时间 (2018-04-08 09:23)
                    from_station = j['stationTrainDTO']['from_station_name']  # 出发地
                    to_station = j['stationTrainDTO']['to_station_name']  # 目的地
                    print('乘客' + str(
                        ticket_num) + ':' + pass_name + date + from_station + to_station + train_code + sequence_no + seat_type_name + seat_name + price + ticket_status_name,
                          sep='  ')
                    ticket_num += 1
                order_num += 1
                print('*' * 80)
            return html_query

    def chooseticket(self, order, passenger, html_query):
        '''选择退哪张'''
        order_select = html_query['data']['OrderDTODataList'][int(order) - 1]
        ticket_select = html_query['data']['OrderDTODataList'][int(order) - 1]['tickets'][int(passenger) - 1]
        if '已退票' in ticket_select['ticket_status_name']:
            print('此车票已经退过了,亲~')
            exit()

        sequence_no = ticket_select['sequence_no']  # 订单号
        pass_name = ticket_select['passengerDTO']['passenger_name']  # 乘客姓名
        id_type = ticket_select['passengerDTO']['passenger_id_type_code']  # id类型
        id_no = ticket_select['passengerDTO']['passenger_id_no']  # id号码
        ticket_status_name = ticket_select['ticket_status_name']  # 订单状态
        seat_type_name = ticket_select['seat_type_name']  # 座位类型
        seat_name = ticket_select['seat_name']  # 座位号
        seat_no = ticket_select['seat_no']  # 座位号
        price = ticket_select['str_ticket_price_page']  # 票价
        ticket_no = ticket_select['ticket_no']  # 车票号
        train_no = ticket_select['stationTrainDTO']['trainDTO']['train_no']  # 车次号
        train_code = ticket_select['stationTrainDTO']['station_train_code']  # 车次号
        train_date = ticket_select['train_date']  # 时间号
        batch_no = ticket_select['batch_no']  # 批号
        coach_no = ticket_select['coach_no']  # 车厢号
        coach_name = ticket_select['coach_name']  # 车厢号
        date = ticket_select['start_train_date_page']  # 乘车日期+时间
        from_station = ticket_select['stationTrainDTO']['from_station_name']  # 出发地
        from_station_telecode = ticket_select['stationTrainDTO']['from_station_telecode']  # 出发地简拼
        to_station = ticket_select['stationTrainDTO']['to_station_name']  # 目的地
        to_station_telecode = ticket_select['stationTrainDTO']['to_station_telecode']  # 目的地简拼
        start_time = ticket_select['stationTrainDTO']['start_time']  # 运营时间
        print(
            '您要退票的信息为:' + pass_name + date + from_station + to_station + train_code + sequence_no + seat_type_name + seat_name + price + ticket_status_name,
            sep='  ')
        return train_no, train_date, train_code, to_station_telecode, to_station, date, start_time, sequence_no, seat_type_name, seat_no, seat_name, pass_name, id_type, id_no, from_station_telecode, from_station, coach_no, coach_name, batch_no

    def cancelticket(self, train_no, train_date, train_code, to_station_telecode, to_station, date, start_time,
                     sequence_no, seat_type_name, seat_no, seat_name, pass_name, id_type, id_no, from_station_telecode,
                     from_station, coach_no, coach_name, batch_no):
        '''提交退票'''
        form_return = {
            'train_no': train_no,
            'train_date': train_date,
            'train_code': train_code,
            'to_station_telecode': to_station_telecode,
            'to_station_name': to_station,
            'start_train_date_page': date,
            'start_time': start_time,
            'sequence_no': sequence_no,
            'seat_type_name': seat_type_name,
            'seat_no': seat_no,
            'seat_name': seat_name,
            'passenger_name': pass_name,
            'id_type': id_type,  # id: '1':身份证类型
            'id_no': id_no,  # id号码
            'from_station_telecode': from_station_telecode,
            'from_station_name': from_station,
            'coach_no': coach_no,
            'coach_name': coach_name,
            'batch_no': batch_no,
            '_json_att': ''
        }
        global req
        html_return = req.post(self.url_return, headers=self.head_query, data=form_return).json()
        print(html_return)
        if html_return['status'] == True:
            print('提交退票信息成功!')
        else:
            print('提交退票信息失败!')
            exit()
        # 用户是否继续退票:
        i = input('是否确定退票?(Y or N):')
        if i == 'Y' or i == 'y':
            pass
        else:
            exit()
        # 最终退票
        form_end = {
            '_json_att': ''
        }
        html_end = req.post(self.url_end, data=form_end, headers=self.head_query).json()
        print(html_end)
        if html_return['status'] == True:
            print('确认退票成功!')
            print('恭喜您退票成功!')
        else:
            print('确认退票失败!')
            exit()


def order():
    '''订票函数'''
    # 用户输入购票信息:
    from_station = input('请输入您要购票的出发地(例:北京):')
    # from_station = '北京'
    to_station = input('请输入您要购票的目的地(例:上海):')
    # to_station = '上海'
    date = input('请输入您要购票的乘车日期(例:2019-03-06):')
    # date = '2019-05-15'
    # 余票查询
    query = Leftquery()
    result = query.query(from_station, to_station, date)
    # 开始订票
    login = Login()
    login.get_rail_deviceid()
    login.showimg()
    # 填写验证码
    print('  =============================================================== ')
    print('   根据打开的图片识别验证码后手动输入，输入正确验证码对应的位置 ')
    print('     --------------------------------------')
    print('            1  |  2  |  3  |  4 ')
    print('     --------------------------------------')
    print('            5  |  6  |  7  |  8 ')
    print('     --------------------------------------- ')
    print(' =============================================================== ')
    answer_num = input('请填入验证码(序号为1~8,中间以逗号隔开,例:1,2):')
    login.captcha(answer_num)
    login.login(answer_num)
    # 提交订单
    order = Order()
    order.auth()
    # 用户选择要购买的车次的序号
    train_number = input('请输入您要购买的车次的序号(例如:6):')
    # 提交订单
    order.order(result, train_number, from_station, to_station, date)
    # 检查订单
    content = order.price()  # 打印出票价信息
    passengers = order.passengers(content[8])  # 打印乘客信息
    # 选择乘客和座位
    passengers_name = input('请选择您要购买的乘客编号(例:1,4):')
    choose_seat = input('请选择您要购买的座位类型(例:商务座):')
    pass_info = order.chooseseat(passengers, passengers_name, choose_seat, content[8])
    # 查看余票数
    order.leftticket(content[0], content[1], content[2], pass_info[2], content[3], content[4], content[5], content[6],
                     content[7], content[8])
    # 是否确认购票
    order.sure()
    # 最终确认订单
    order.confirm(pass_info[0], pass_info[1], content[9], content[5], content[6], content[7], content[8])

def cancelorder():
    '''取消订单函数'''
    cancelorder = Cancelorder()
    cancelorder.get_rail_deviceid()
    cancelorder.showimg()
    # 填写验证码
    print('  =============================================================== ')
    print('   根据打开的图片识别验证码后手动输入，输入正确验证码对应的位置 ')
    print('     --------------------------------------')
    print('            1  |  2  |  3  |  4 ')
    print('     --------------------------------------')
    print('            5  |  6  |  7  |  8 ')
    print('     --------------------------------------- ')
    print(' =============================================================== ')
    answer_num = input('请填入验证码(序号为1~8,中间以逗号隔开,例如:3,6,8):')
    cancelorder.captcha(answer_num)
    cancelorder.login(answer_num)
    # 查询订单
    cancelorder.auth()
    # 取消订单
    orderinfo = cancelorder.orderinfo()
    cancelorder.confirmcancel(orderinfo)

def cancelticket():
    '''退票函数'''
    cancelticket = Cancelticket()
    cancelticket.get_rail_deviceid()
    cancelticket.showimg()
    # 填写验证码
    print('  =============================================================== ')
    print('   根据打开的图片识别验证码后手动输入，输入正确验证码对应的位置 ')
    print('     --------------------------------------')
    print('            1  |  2  |  3  |  4 ')
    print('     --------------------------------------')
    print('            5  |  6  |  7  |  8 ')
    print('     --------------------------------------- ')
    print(' =============================================================== ')
    answer_num = input('请填入验证码(序号为1~8,中间以逗号隔开,例:2,3):')
    cancelticket.captcha(answer_num)
    cancelticket.login(answer_num)
    # 查询历史订单
    cancelticket.auth()
    querytype = input('请选择查询方式(1:按订票日期查询 2:按乘车日期查询):')
    startdate = input('请输入查询起始日期(如:2019-01-16):')
    enddate = input('请输入查询最终日期(如:2019-01-16):')
    train_info = input('请输入乘客姓名(例:小明)或车次号(例:K1561)或订单号(例:EF159626),也可以不填跳过(直接按回车键):')
    queryinfo = cancelticket.queryorder(querytype, startdate, enddate, train_info)
    # 用户选择要退哪张票
    order = input('请选择要退票的订单编号(例:1):')
    passenger = input('请选择要退票的乘客编号(例:1):')
    ticket_info = cancelticket.chooseticket(order, passenger, queryinfo)
    cancelticket.cancelticket(ticket_info[0], ticket_info[1], ticket_info[2], ticket_info[3], ticket_info[4],
                              ticket_info[5], ticket_info[6], ticket_info[7], ticket_info[8], ticket_info[9],
                              ticket_info[10], ticket_info[11], ticket_info[12], ticket_info[13], ticket_info[14],
                              ticket_info[15], ticket_info[16], ticket_info[17], ticket_info[18])

def select():
    print('1.购票  2.取消订单  3.退票')
    print('*' * 69)
    func = input('请输入您要操作的选项(例:1):')
    global username, password
    if func == '1':
        username = input('请输入您的12306账号名称:')
        password = input('请输入您的12306账号密码:')
        order()
        exit()
    if func == '2':
        username = input('请输入您的12306账号名称:')
        password = input('请输入您的12306账号密码:')
        cancelorder()
        exit()
    if func == '3':
        username = input('请输入您的12306账号名称:')
        password = input('请输入您的12306账号密码:')
        cancelticket()
        exit()
    else:
        print('输入有误,请重新输入...')
        print('*' * 69)
        select()


if __name__ == '__main__':
    print('*' * 30 + '12306购票' + '*' * 30)
    select()
