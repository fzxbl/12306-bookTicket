# coding:utf-8
import login,re,time
import requests
from json import dumps
import urllib.parse
from ticketInfo import *
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
class BookTicket:

	def __init__(self):
		self.proxy = {'http': '127.0.0.1:9999', 'https': '127.0.0.1:9999'}
		# print(self.s.cookies.get_dict())
		obj = TicketInfo()
		self.stationDict=obj.getStationDict()
		self.queryParams,self.startStation,self.destination=obj.getQueryParams()
		obj.getTicketInfo(self.queryParams)
		self.secretStrList,self.fromStation,self.toStation,self.trainNum,self.train,self.fromStationCode,self.toStationCode,self.leftTicket,self.trainLocation,self.dWall=obj.displayInfo()
		time.sleep(5)
		obj = login.Login()
		self.s = obj.login()
		#1 商务座 2 一等座 3 二等座 4 高级软卧 5 动卧 6 软卧 7 硬卧 8 软座 9 硬座
		self.siteCode = {
			'9': '1',
			'8': '2',
			'7': '3',
			'6': '4',
			'4': '6',
			'1': '9',
			'2': 'M',
			'3': 'O',
			'5': 'F'
		}
		self.s.headers = {
			'Accept': '*/*',
			'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
			'Accept-Encoding': 'gzip, default',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'X-Requested-With': 'XMLHttpRequest',
			'Host': 'kyfw.12306.cn',
			'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36 BIDUBrowser/8.8'
		}
		cookies={
				 '_jc_save_fromStation':str.upper(dumps(self.startStation))[1:-1].replace('\\','%')+'%2C'+self.stationDict[self.startStation],
				 '_jc_save_toStation':str.upper(dumps(self.destination)[1:-1]).replace('\\','%')+'%2C'+self.stationDict[self.destination],
			  	 '_jc_save_fromDate':self.queryParams['leftTicketDTO.train_date'],
				 '_jc_save_toDate':time.strftime('%Y-%m-%d',time.localtime(time.time())),
				 '_jc_save_wfdc_flag':'dc',
				 '_jc_save_showIns': 'true',
				 'current_captcha_type': 'Z'
		}
		requests.utils.add_dict_to_cookiejar(self.s.cookies, cookies)
		# self.s.cookies.set('_passport_session', None)
		# self.s.cookies.set('uamtk', None)

	# 提交订单
	def submitOrderRequest(self):
		self.trainIndex=int(input('请输入要选择的序号：'))
		if self.secretStrList[self.trainIndex]=='预定':
			print('不可预定')
		else:
			data={
				'secretStr':urllib.parse.unquote(self.secretStrList[self.trainIndex]),
				'train_date':self.queryParams['leftTicketDTO.train_date'],
				'back_train_date':time.strftime('%Y-%m-%d',time.localtime(time.time())),
				'tour_flag':'dc',
				'purpose_codes':'ADULT',
				'query_from_station_name':urllib.parse.quote(self.startStation),
				'query_to_station_name':urllib.parse.quote(self.destination),
				'undefined': ''
			}
			try:
				res=self.s.post('https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest',data=data)
				if res.json()['data']=='N':
					print('提交订单请求成功')
			except Exception as e:
				print(e)
				self.submitOrderRequest()
			#提交订单完毕
	def confirmPassenger(self):
		try:
			res=self.s.post('https://kyfw.12306.cn/otn/confirmPassenger/initDc',data={'_json_att=':''})
			reg=r"var globalRepeatSubmitToken = '(.*?)'"
			RepeatSubmitToken=re.findall(reg,res.text)
			reg2=r"'key_check_isChange':'(.*?)'"
			self.keyCheckIsChange=re.findall(reg2,res.text)
			self.repeatSubmitToken=RepeatSubmitToken
		except Exception as e:
			print(e)
			self.confirmPassenger()
	def getPassenger(self):
		try:
			res=self.s.post('https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs',data={'REPEAT_SUBMIT_TOKEN':self.repeatSubmitToken})
			self.passengerList=res.json()['data']['normal_passengers']
		except Exception as e:
			print(e)
			self.getPassenger()
		print('发现{}名联系人：'.format(len(self.passengerList)))
		j=0
		for i in self.passengerList:
			print(j,i['passenger_name'])
			j+=1
		return self.passengerList
	def checkOrderInfo(self):
		index=int(input('请选择联系人：'))
		print('1 商务座 2 一等座 3 二等座 4 高级软卧 5 动卧 6 软卧 7 硬卧 8 软座 9 硬座')
		self.seat=input('请选择座次：')
		self.chosedPassenger=self.passengerList[index]
		data={
			'cancel_flag':'2',
			'bed_level_order_num':'000000000000000000000000000000',
			'passengerTicketStr':'{},{},{},{},1,{},{},N'.format(self.siteCode[self.seat],self.chosedPassenger['passenger_flag'],self.chosedPassenger['passenger_id_type_code'],self.chosedPassenger['passenger_name'],self.chosedPassenger['passenger_id_no'],self.chosedPassenger['mobile_no']),
			'oldPassengerStr':'{},1,{},3_'.format(self.chosedPassenger['passenger_name'],self.chosedPassenger['passenger_id_no']),
			'tour_flag':'dc',
			'randCode': '',
			'_json_att': '',
			'REPEAT_SUBMIT_TOKEN':self.repeatSubmitToken
		}
		try:
			res=self.s.post('https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo',data=data)
			if res.json()['data']['submitStatus']==True:
				print('确认订单成功')
		except Exception as e:
			print(e)
			self.checkOrderInfo()
	# def getQueueCount(self):
	# 	data={
	# 		'train_date':'Sun Oct 15 2017 00:00:00 GMT+0800',#此处还需修改
	# 		'train_no':self.trainNum[self.trainIndex],
	# 		'stationTrainCode':self.train[self.trainIndex],
	# 		'seatType':'O',
	# 		'fromStationTelecode':self.fromStationCode[self.trainIndex],
	# 		'toStationTelecode':self.toStationCode[self.trainIndex],
	# 		'leftTicket':self.leftTicket[self.trainIndex],
	# 		'purpose_codes':'00',
	# 		'train_location':self.trainLocation[self.trainIndex],
	# 		'REPEAT_SUBMIT_TOKEN':self.repeatSubmitToken
	# 	}
	# 	print(data)
	# 	res=self.s.post('https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount',data=data,verify=False)
	# 	print(res.text)
	def confirmSingleForQueue(self):
		data = {
			'passengerTicketStr': '{},{},{},{},1,{},{},N'.format(self.siteCode[self.seat],self.chosedPassenger['passenger_flag'],self.chosedPassenger['passenger_id_type_code'],self.chosedPassenger['passenger_name'],self.chosedPassenger['passenger_id_no'],self.chosedPassenger['mobile_no']),
			'oldPassengerStr': '{},1,{},3_'.format(self.chosedPassenger['passenger_name'],self.chosedPassenger['passenger_id_no']),
			'purpose_codes': '00',
			'leftTicketStr': self.leftTicket[self.trainIndex],
			'train_location': self.trainLocation[self.trainIndex],
			'seatDetailType':'000',
			'roomType': '00',
			'key_check_isChange':self.keyCheckIsChange,
			# 'dwAll' :self.dWall[self.trainIndex],
			'dwAll': 'N',
			'_json_att': '',
			'choose_seats': '',
			'randCode': '',
			'REPEAT_SUBMIT_TOKEN': self.repeatSubmitToken
		}
		try:
			res=self.s.post('https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue',data=data,verify=False)
			if res.json()['data']['submitStatus']==True:
				print('订票成功，请登录12306付款')
		except Exception as e:
			print(e)
			self.confirmSingleForQueue()
	# def queryOrderWaitTime(self):
	# 	params={
	# 	'random' : '1507098093943',
	# 	'tourFlag': 'dc',
	# 	'REPEAT_SUBMIT_TOKEN': self.repeatSubmitToken
	# 	}
	# 	self.s.get('https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime',params=params)
if __name__=='__main__':
	obj=BookTicket()
	obj.submitOrderRequest()
	obj.confirmPassenger()
	obj.getPassenger()
	obj.checkOrderInfo()
	# obj.getQueueCount()
	obj.confirmSingleForQueue()