import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = "http://tvl.ctvba.org.tw/fixtures-results/"
res = requests.get(url)
res.encoding = "utf-8"
soup = BeautifulSoup(res.text, "html.parser")
table = soup.find("div", {"class": "sportspress sp-widget-align-left"}).find("div", {"class": "sp-template sp-template-event-blocks"}).find("div", {"class": "sp-table-wrapper"}).find("table", {"class": "sp-event-blocks sp-data-table sp-paginated-table"}).find("tbody")

current_date = datetime.now()

for i in table.find_all("tr"):
	link = i.find("h4", {"class": "sp-event-title"}).a["href"] # 再對爬到的網址連結進行爬蟲 也就是爬兩層
	rsp = requests.get(link)
	rsp.encoding = "utf-8"
	sp = BeautifulSoup(rsp.text, "html.parser")
	tr = sp.find("table", {"class": "sp-event-details sp-data-table sp-scrollable-table"}).find("tbody").find("tr")
	text = list(tr.stripped_strings)
	# stripped_strings 用法參考 https://www.dotblogs.com.tw/YiruAtStudio/2020/11/12/203032
	date = datetime.strptime(text[0], "%Y/%m/%d")
	if date >= current_date:
		print(text[0], end=" ") # 日期
		print(text[1]) # 時間
		location = sp.find("table", {"class": "sp-data-table sp-event-venue"}).find("thead").find("tr")
		print(location.text.strip()) # 舉辦地點
		team = sp.find("header", {"class": "entry-header"}).text.strip().split(" vs ")
		print(team[0], end=" ") # 參賽隊伍1
		print(team[1]) # 參賽隊伍2
		print()