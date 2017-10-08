# coding:utf-8
import  requests,re,time,random
from json import loads
from twilio.rest import Client
from prettytable import PrettyTable
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
class TicketInfo:
	def __init__(self):
		self.s=requests.session()
		self.resultList=[]
		self.queryParams={}
		self.stationDict = {}
		self.station = []
		self.stationCode = []
		self.stationCodeDict={}
		self.secretStr=[]
		self.fromStation=[]
		self.toStation=[]
		self.trainNum=[]
		self.train=[]
		self.fromStationCode=[]
		self.toStationCode=[]
		self.leftTicket=[]
		self.trainLocation=[]
		self.dWall=[]
		self.moniterDict={'1':32,'2':31,'3':30,'4':21,'5':23,'6':26,'7':28,'8':29}
		self.seatTypeDict={32:'商务座',31:'一等座',30:'二等座',21:'高级软卧',23:'软卧',26:'硬卧',28:'硬座',29:'无座'}
		#21 高级软卧  23软卧 26硬卧 28 硬座 29 无座 30 二等座 31 一等座 32 商务座
		self.s.headers={
					  'Host':'kyfw.12306.cn',
					  'Referer':'http://www.12306.cn/mormhweb/',
					  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36 BIDUBrowser/8.8'
					  }
	def getStationDict(self):
		try:
			response = requests.get('https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9027', verify=False)
			content = response.text
		except Exception as e:
			print(e)
			self.getStationDict()
		reg = r'@.*?\|(.*?)\|(.*?)\|'
		stationList = re.findall(reg, content)
		j = 0
		for i in stationList:
			self.stationDict[i[0]]=i[1]
			j += 1
		self.stationCodeDict={v:k for k,v in self.stationDict.items()}
		return self.stationDict
	def getStationInfo(self,station):
		temp=self.stationDict[station]
		return self.stationCodeDict[temp], temp
	def getQueryParams(self):
		date = input('请输入乘车日期，如:2017-9-30\n>>>')
		startStaion = input('请输入出发城市，非站名:\n>>>')
		startStaion,startStaionCode=self.getStationInfo(startStaion)
		destination = input('请输入目的城市，非站名:\n>>>')
		destination,destinationCode = self.getStationInfo(destination)
		# type = input('Please enter your the type of ticket you want to query (1 for adult and 2 for student):\n>>>')
		self.queryParams={'leftTicketDTO.train_date':date,
				'leftTicketDTO.from_station':startStaionCode,
				'leftTicketDTO.to_station':destinationCode,
				'purpose_codes':'ADULT'}
		return self.queryParams,startStaion,destination
	def getTicketInfo(self,queryParams):
		requests.utils.add_dict_to_cookiejar(self.s.cookies,{
			'fp_ver': '4.5.1',
			' RAIL_EXPIRATION': str(int(round(time.time() * 1000))),
			'RAIL_DEVICEID': 'lRJS4LUFlzx7hr4FQRpeJJpsadV-NKiN74dplfA37atNLMDEbaQ5C6J7rs1hRym9o8t_LtIR_0jv0kqT7Os6tHJkRPeq_rm5Xk9445hd7HyNMxnS-2CHmLBB9Mjid_JCYsuaYzPK-oM8CWUUNG5Ebdrg3bvyX9ez'
		})
		while 1:
			try:
				response=self.s.get('https://kyfw.12306.cn/otn/leftTicket/queryX',params=queryParams,verify=False,timeout=5)
				result=loads(response.text)
				self.resultList=result['data']['result']
				break
			except Exception as e:
				print('查询失败，尝试重新查询',e)
				time.sleep(5)
	def displayInfo(self):
		table=PrettyTable(['序号','车次','出发地', '目的地', '出发时间', '到达时间' ,'商务座' ,'一等座', '二等座' ,'高级软卧', '软卧', '硬卧', '硬座', '无座'])
		j=0
		for i in self.resultList:
			strList=i.split('|')
			self.secretStr.append(strList[0])
			self.fromStation.append(self.stationCodeDict[strList[6]])
			self.toStation.append(self.stationCodeDict[strList[7]])
			self.fromStationCode.append(strList[6])
			self.toStationCode.append(strList[7])
			self.trainNum.append(strList[2])
			self.train.append(strList[3])
			self.leftTicket.append(strList[12])
			self.trainLocation.append(strList[15])
			self.dWall.append(strList[11])
			table.add_row([j,strList[3],self.stationCodeDict[strList[6]],self.stationCodeDict[strList[7]],strList[8],strList[9],strList[32],strList[31],strList[30],strList[21],strList[23],strList[26],strList[28],strList[29]])
			j+=1
		print(table)
		return self.secretStr,self.fromStation,self.toStation,self.trainNum,self.train,self.fromStationCode,self.toStationCode,self.leftTicket,self.trainLocation,self.dWall
		# 2 trainNum 3 车次 6 出发车站 7 到达车站 8 出发时间 9 到达时间12 leftTicket 15 trainLocation 21 高级软卧  23软卧 26硬卧 28 硬座 29 无座 30 二等座 31 一等座 32 商务座
	def moniter(self,trainNum,argsList,phoneNum):
		# phoneNum=input('请输入你的接收短信提醒手机号:')
		self.getStationDict()
		self.getQueryParams()
		ticketLeft=[]
		flag=1
		while 1:
			self.getTicketInfo(self.queryParams)
			for i in self.resultList:
				strList=i.split('|')
				if strList[3]!=trainNum:
					continue
				else:
					for item in argsList:
						if strList[self.moniterDict[item]]=='无' or strList[self.moniterDict[item]]=='':
							if flag:
								found=False
						else:
							if flag:
								found=True
								flag=0
							ticketLeft.append(self.moniterDict[item])
							continue
					break
			if not found:
				print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'已为您刷新余票，暂未发现{}的您指定的任何余票'.format(trainNum))
				time.sleep(5)
				continue
			else:
				seat=[]
				for i in ticketLeft:
					seat.append(self.seatTypeDict[i])
					print(self.seatTypeDict[i],'有票啦！')
				ACCOUNT_SID = 'ACbd92f23ff48bbecb3cf9b9bfcc8f4f23'
				AUTH_TOKEN = 'ee370c586f836b834b485fd760e97dc5'
				client = Client(ACCOUNT_SID, AUTH_TOKEN)
				recipient = '+86'+phoneNum  #  接收短信的手机
				text = '已为您查询到{}的{}余票，请尽快买票'.format(trainNum,seat)
				#  这里的from_参数是一个手机号, 网站免费提供给你的
				client.messages.create(
					recipient,
					from_='+12014706119',
					body=text
				)
				return 0


if __name__=='__main__':
	obj=TicketInfo()
	# obj.getStationDict()
	# obj.getQueryParams()
	# obj.getTicketInfo(obj.queryParams)
	# obj.displayInfo()
	# print('1 商务座 2 一等座 3 二等座 4 高级软卧 5 软卧 6 硬卧 7 硬座 8 无座 ')
	# temp=input('请输入你想监视的座次，例如：1,2,3\n>>>')
	# argsList=temp.split(',')
	obj.moniter('G315',['3'],'18071029349')