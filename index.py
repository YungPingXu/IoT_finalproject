from flask import Flask, render_template, request
import requests
import DAN
import socket
import threading
from time import sleep

app = Flask(__name__) # 初始化 Flask 類別成為 instance

@app.route("/") # 路由和處理函式配對
def index():
    return render_template("index.html")

def location_IDF_thread():
	ServerURL = 'https://5.iottalk.tw'
	Reg_addr = None
	mac_addr = 'user-location'
	Reg_addr = mac_addr
	DAN.profile['dm_name'] = 'user-location'
	DAN.profile['df_list'] = ['location-IDF', 'final-result-ODF']
	DAN.profile['d_name'] = "user-location"
	DAN.device_registration_with_retry(ServerURL, Reg_addr)
	print("dm_name is ", DAN.profile['dm_name'])
	print("Server is ", ServerURL)
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.bind(("127.0.0.1", 8395))
	while True:
		try:
			data, info = sock.recvfrom(1024)
			value = data.decode("utf-8")
			user = value.split(" ")
			DAN.push('location-IDF', float(user[0]), float(user[1]), float(user[2]))
			sleep(1)
			result = DAN.pull('final-result-ODF')
			if result != None:
				sock.sendto(result[0].encode("utf-8"), ("127.0.0.1", 8495))
		except KeyboardInterrupt:
			print("\n\nDeregister " + DAN.profile['d_name'] + " !!!\n",  flush=True)
			DAN.deregister()
			sock.close()
			break

@app.route("/user-location")
def location_IDF():
	th = threading.Thread(target=location_IDF_thread)
	th.daemon = True
	th.start()
	return "user-location"

@app.route("/get-result", methods=["GET"])
def get_result():
	url = "https://maps.googleapis.com/maps/api/staticmap?center="
	center = request.args.get("center")
	zoom = request.args.get("zoom")
	size = request.args.get("size")
	key = request.args.get("key")
	distance = request.args.get("distance")
	url += center + "&zoom=" + zoom + "&size=" + size + "&key=" + key
	img = requests.get(url)
	with open("static/" + center + ".png", "wb") as f:
		f.write(img.content)
	user = request.args.get("lat") + " " + request.args.get("lon") + " " + str(distance)
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.sendto(user.encode("utf-8"), ("127.0.0.1", 8395))
	sleep(1)
	sock2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock2.bind(("127.0.0.1", 8495))
	sleep(1)
	result, info = sock2.recvfrom(50000)
	sock.close()
	sock2.close()
	return result.decode("utf-8")

if __name__ == "__main__": # 判斷自己執行非被當做引入的模組，因為 __name__ 這變數若被當做模組引入使用就不會是 __main__
	app.debug = True
	app.run()