import DAN
import socket
import time
# ServerURL = 'http://demo.iottalk.tw' #with no secure connection
#  注意你用的 IoTtalk 伺服器網址或 IP  #  https://goo.gl/6jtP41
ServerURL = 'https://5.iottalk.tw' # with SSL secure connection
# ServerURL = 'https://Your_DomainName' #with SSL connection  (IP can not be used with https)
Reg_addr = None #if None, Reg_addr = MAC address #(本來在 DAN.py 要這樣做 :-)
# Note that Reg_addr 在以下三句會被換掉! # the mac_addr in DAN.py is NOT used
mac_addr = 'location.IN' #+ str( random.randint(100,999 ) )  # put here for easy to modify :-)
# 若希望每次執行這程式都被認為同一個 Dummy_Device, 要把上列 mac_addr 寫死, 不要用亂數。
Reg_addr = mac_addr   # Note that the mac_addr generated in DAN.py always be the same cause using UUID !
DAN.profile['dm_name'] = 'user_location'   # you can change this but should also add the DM in server
DAN.profile['df_list'] = ['location-IDF', 'final-result-ODF']   # Check IoTtalk to see what IDF/ODF the DM has
DAN.profile['d_name'] = "location.IN" #+ str( random.randint(100,999 ) ) +"_"+ DAN.profile['dm_name'] # None
DAN.device_registration_with_retry(ServerURL, Reg_addr)
print("dm_name is ", DAN.profile['dm_name'])
print("Server is ", ServerURL)
# global gotInput, theInput, allDead    ## 主程式不必宣告 globel, 但寫了也 OK

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 8195))

while True:
	try:
		data, info = sock.recvfrom(1024)
		if data.decode("utf-8") == "exit":
			print("\n\nDeregister " + DAN.profile['d_name'] + " !!!\n",  flush=True)
			DAN.deregister()
			sock.close()
			break
		value = data.decode("utf-8")
		latlon = value.split(" ")
		DAN.push('location-IDF', latlon[0], latlon[1])
		time.sleep(1)
		pull = DAN.pull('final-result-ODF')
		if pull != None:
			print(pull[0])
	except KeyboardInterrupt:
		print("\n\nDeregister " + DAN.profile['d_name'] + " !!!\n",  flush=True)
		DAN.deregister()
		sock.close()
		break