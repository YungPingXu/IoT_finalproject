import DAN
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import threading
import sys
from datetime import datetime
from haversine import haversine

ServerURL = "https://5.iottalk.tw"
Reg_addr = None
mac_addr = "middle-server"
Reg_addr = mac_addr
DAN.profile["dm_name"] = "middle-server"
DAN.profile["df_list"] = ["crawl-IDF", "crawl-ODF", "location-ODF", "final-result-IDF"]
DAN.profile["d_name"] = "middle-server"
DAN.device_registration_with_retry(ServerURL, Reg_addr)
print("dm_name is ", DAN.profile["dm_name"])
print("Server is ", ServerURL)

allDead = False
game_table = []
current_date = datetime.now()

def write_data():
	data = DAN.pull("crawl-ODF")
	if data != None:
		print(data)
		new = True
		with open("game-list.txt", "r", encoding="utf-8") as f:
			for line in f:
				datalist = line.strip().split(" ")
				if datalist[:6] == data:
					new = False
					break
		if new:
			print("new")
			url = 'https://maps.googleapis.com/maps/api/geocode/json'
			params = {'key': 'your key', 'address': data[3]}
			r = requests.get(url, params=params)
			results = r.json()['results']
			location = results[0]['geometry']['location']
			with open("game-list.txt", "a", encoding="utf-8") as f:
				s = ""
				for i in data:
					s += i + " "
				s += str(location['lat']) + " " + str(location['lng']) + "\n"
				f.writelines(s)

def Pleague():
	print("Crawling the P-league website...")
	url = "https://pleagueofficial.com/schedule-regular-season"
	res = requests.get(url)
	res.encoding = "utf-8"
	soup = BeautifulSoup(res.text, "html.parser")
	global game_table
	for i in soup.find_all("div", {"class": "row mx-0"}):
		text = list(i.stripped_strings)
		if len(text) in (21, 22): # if len(text) == 21 or len(text) == 22
			tmplist = []
			tmplist.append("P-league")
			tmplist.append(text[0]) # 日期
			tmplist.append(text[2]) # 時間
			tmplist.append(text[10]) # 舉辦地點
			tmplist.append(text[4]) # 參賽隊伍1
			tmplist.append(text[17]) # 參賽隊伍2
			if tmplist not in game_table:
				game_table.append(tmplist)
				DAN.push("crawl-IDF", "P-league", text[0], text[2], text[10], text[4], text[17])
				sleep(0.5)
				write_data()

def SBL():
	print("Crawling the SBL website...")
	url = "https://sleague.tw/gameList.html"
	driver = webdriver.Chrome() # 啟動瀏覽器
	driver.get(url) # 取得網頁原始碼
	sleep(1)
	driver.refresh() # 重新刷新網頁
	sleep(1)
	driver.refresh() # 重新刷新網頁
	sleep(2)
	soup = BeautifulSoup(driver.page_source, "html.parser")
	table = soup.find("table", {"class": "table table-hover same-bg"}).find("tbody")
	sleep(1)
	driver.quit() # 關閉瀏覽器
	for i in table.find_all("tr"):
		text = list(i.stripped_strings)
		tmplist = []
		tmplist.append("SBL")
		tmplist.append(text[1]) # 日期
		tmplist.append(text[2]) # 時間
		tmplist.append(text[3]) # 舉辦地點
		team = str(text[4]).replace("\t", "").replace("\n", " ").replace(" ", "").split("vs.")
		tmplist.append(team[0]) # 參賽隊伍1
		tmplist.append(team[1]) # 參賽隊伍2
		date = datetime.strptime(text[1], "%Y/%m/%d")
		if tmplist not in game_table and date >= current_date:
			game_table.append(tmplist)
			DAN.push("crawl-IDF", "SBL", text[1], text[2], text[3], team[0], team[1])
			sleep(0.5)
			write_data()

def TVL():
	print("Crawling the TVL website...")
	url = "http://tvl.ctvba.org.tw/fixtures-results/"
	res = requests.get(url)
	res.encoding = "utf-8"
	soup = BeautifulSoup(res.text, "html.parser")
	table = soup.find("div", {"class": "sportspress sp-widget-align-left"}).find("div", {"class": "sp-template sp-template-event-blocks"}).find("div", {"class": "sp-table-wrapper"}).find("table", {"class": "sp-event-blocks sp-data-table sp-paginated-table"}).find("tbody")
	for i in table.find_all("tr"):
		link = i.find("h4", {"class": "sp-event-title"}).a["href"] # 再對爬到的網址連結進行爬蟲 也就是爬兩層
		rsp = requests.get(link)
		rsp.encoding = "utf-8"
		sp = BeautifulSoup(rsp.text, "html.parser")
		tr = sp.find("table", {"class": "sp-event-details sp-data-table sp-scrollable-table"}).find("tbody").find("tr")
		text = list(tr.stripped_strings)
		tmplist = []
		tmplist.append("TVL")
		tmplist.append(text[0]) # 日期
		tmplist.append(text[1]) # 時間
		location = sp.find("table", {"class": "sp-data-table sp-event-venue"}).find("thead").find("tr")
		tmplist.append(location.text.strip()) # 舉辦地點
		team = sp.find("header", {"class": "entry-header"}).text.strip().split(" vs ")
		tmplist.append(team[0]) # 參賽隊伍1
		tmplist.append(team[1]) # 參賽隊伍2
		date = datetime.strptime(text[0], "%Y/%m/%d")
		if tmplist not in game_table and date >= current_date:
			game_table.append(tmplist)
			DAN.push("crawl-IDF", "TVL", text[0], text[1], location.text.strip(), team[0], team[1])
			sleep(0.5)
			write_data()

def routine():
	global allDead, current_date
	while True:
		try:
			current_date = datetime.now()
			SBL()
			TVL()
			Pleague()
			sleep(1200)
		except KeyboardInterrupt:
			allDead = True
			print("\n\nDeregister " + DAN.profile["d_name"] + " !!!\n",  flush=True)
			DAN.deregister()
			sys.stdout = sys.__stdout__
			print(" Thread say Bye bye ---------------", flush=True)
			sys.exit()
try:
	sleep(10) # 趁這時關聯進iottalk的project裡
	th = threading.Thread(target=routine)
	th.daemon = True
	th.start()
except KeyboardInterrupt:
	print("\n\nDeregister " + DAN.profile["d_name"] + " !!!\n",  flush=True)
	DAN.deregister()
	sys.exit()

while True:
	try:
		if allDead: break
		user = DAN.pull("location-ODF")
		if user != None:
			print(user)
			point = (user[0], user[1])
			distance = user[2]
			tmp = "<table><tr><th>球賽種類</th><th>日期</th><th>時間</th><th>舉辦地點</th><th>參賽隊伍</th></tr>"
			with open("game-list.txt", "r", encoding="utf-8") as f:
				for line in f:
					data = line.strip().split(" ")
					p = (float(data[6]), float(data[7]))
					if haversine(point, p) <= distance: # km
						tmp += "<tr><td>" + data[0] + "</td><td>" + data[1] + "</td><td>" + data[2] + "</td><td>" + data[3] + "</td><td>" + data[4] + " vs. " + data[5] + "</td></tr>"
			tmp += "</table>"
			DAN.push("final-result-IDF", tmp)
		sleep(0.5)
	except KeyboardInterrupt:
		print("\n\nDeregister " + DAN.profile["d_name"] + " !!!\n",  flush=True)
		DAN.deregister()
		sys.exit()