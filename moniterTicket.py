from ticketInfo import *
obj=TicketInfo()
trainNum=input('请输入你监控的车次：\n>>>')
print('1 商务座 2 一等座 3 二等座 4 高级软卧 5 软卧 6 硬卧 7 硬座 8 无座 ')
seatType=input('请输入你想监视的座次，以英文逗号分隔，例如：1,2,3\n>>>').split(',')
# seatType=seatType.split(',')
phoneNum=input('请输入接收通知短信手机号：\n>>>')
obj.moniter(trainNum,seatType,phoneNum)