from apscheduler.schedulers.blocking import BlockingScheduler
import requests

sched = BlockingScheduler()

@sched.scheduled_job("interval", minutes=10)
def timed_job():
    print("awake app every 10 minutes.")
    url = "https://iot-final-project.herokuapp.com/"
    requests.get(url)

sched.start()