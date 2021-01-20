import requests
from bs4 import BeautifulSoup

url = "https://pleagueofficial.com/schedule-regular-season"
res = requests.get(url)
res.encoding = "utf-8"
soup = BeautifulSoup(res.text, "html.parser")

for i in soup.find_all("div", {"class": "row mx-0"}):
	print(i.text)
	text = list(i.stripped_strings)
	if len(text) in (21, 22): # if len(text) == 21 or len(text) == 22
		print(text[0], end=" ") # 日期
		print(text[2], end=" ") # 時間
		print(text[10]) # 舉辦地點
		print(text[4], end=" ") # 參賽隊伍1
		print("vs.", end=" ")
		print(text[17], end=" ") # 參賽隊伍2
		print()