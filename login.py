# coding:utf-8
import  requests,requests.cookies,json
from PIL import Image
from json import loads
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
class Login:
	def __init__(self):
		self.s=requests.session()
		self.session = requests.session()
		# self.jar=requests.cookies.RequestsCookieJar()
		self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36 BIDUBrowser/8.8',
				 'Referer':'https://kyfw.12306.cn/otn/login/init',
				 'Host': 'kyfw.12306.cn'}
		self.getCaptcha()
		while self.captchaCheck():
			self.getCaptcha()
		# self.login()
	def getCaptcha(self):
		params={'login_site':'E','module':'login','rand':'sjrand'}
		response=self.s.get('https://kyfw.12306.cn/passport/captcha/captcha-image',params=params,headers=self.headers,verify=False)
		with open('captcha.png', 'wb') as fn:
			fn.write(response.content)
		img = Image.open('captcha.png')
		img.show()
	def captchaCheck(self):
		self.headers['Origin']='https://kyfw.12306.cn'
		answerId=input('please input your answer,for example:1,3,4\n>>>')
		answerIdList=answerId.split(',')
		answerDic={'1':'39,48','2':'112,51','3':'186,45','4':'254,46','5':'40,120','6':'112,120','7':'186,120','8':'254,120'}
		answer=''
		for i in answerIdList:
			answer+=answerDic[i]+','
		data={'answer':answer[:-1],
				'login_site':'E',
				'rand':'sjrand'}
		response=self.s.post('https://kyfw.12306.cn/passport/captcha/captcha-check',data=data,headers=self.headers,verify=False)
		result=loads(response.content)
		if result['result_code']!='4':
			print('验证码校验失败')
			return True
		else:
			print('验证码校验成功')
			return False
	def login(self):
		self.headers['Origin'] = 'https://kyfw.12306.cn'
		userName=input('please input your username:\n>>>')
		pwd=input('please input your password:\n>>>')
		data={'username':userName,
			  'password':pwd,
			  'appid':'otn'}
		response=self.s.post('https://kyfw.12306.cn/passport/web/login',headers=self.headers,data=data,verify=False)
		result = loads(response.text)
		print(result)
		print(result['result_message'])
		self.headers['Referer'] = 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin'
		self.headers['Origin'] = 'https://kyfw.12306.cn'
		response = self.s.post('https://kyfw.12306.cn/passport/web/auth/uamtk', headers=self.headers, verify=False,
							   data={'appid': 'otn'})
		res_json = loads(response.text)
		print(res_json)
		if res_json['result_code'] == 0:
			if res_json["apptk"]:
				a = res_json["apptk"]
			elif len(res_json["newapptk"]) is not 0:
				a = res_json["newapptk"]
		self.s.post('https://kyfw.12306.cn/otn/uamauthclient', params={'tk': a}, verify=False)
		return self.s
if __name__=='__main__':
	obj=Login()
	obj.test()