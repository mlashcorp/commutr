"""
This module performs a commute time estimations using google's distance matrix
API

1) Destinations and Origins are pre-defined in the module. Adding or removing
destinations and/or origins is supported. destinations*origins results will be
generated

2) A list of query times is also defined in the module. It's possible to add or
remove query times, but it's important to consider that the number of API
requests will be destinations*origins*number_of_query_times and should not be
greater than 1000 per day (as per google's free usage conditions).

3) seaborn is used to show averaged commute time for each query time point,
for each combination origin/destination
"""
import argparse
import requests
import time
import schedule
import csv
from time import gmtime, strftime

API_KEY = "AIzaSyAtQd14gP2FvJ08dniIiNo74qrpsI-tH0c"
query_times = ["07:00","08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00",]
origins = [("Estr.+de+Benfica+627,+1500-087+Lisboa","Benfica"),("38.799248, -9.323340","Rua Buganvilias"),("38.816737, -9.254380","Dona Maria")]
destinations = [("38.7544013,-9.1603726","FCUL"),("azambuja","Azambuja")]
query_timeout = 1
scheduler_timeout = 5

"""
Global list containing dictionary entries where the captured data will be stored
  in the following keys:

- origin : contains name of start of commute
- destination : contains name of commute destination
- commute_time : contains the time for the commute in minutes
- time : contain hour and minute of the capture time (hh:mm)
- date : contains day month and year of the capture (dd-mm-YYYY)
"""
empty_payload = {"origin":"","destination":"","commute_time":"","time":"","date":""}

def write_data_to_disk(write_path,payload):
    with open(write_path, "a") as wfile:
        csv_writer = csv.DictWriter(wfile, empty_payload.keys())
        csv_writer.writerow(payload)

def create_url(origin,destination):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins=" + str(origin) +"&destinations="+ str(destination)+ "&key="+API_KEY
    return url

def get_data_from_server(url):
    r = requests.get(url)
    return r.json()

def work_unit(write_path):
    date_label = str(strftime("%d-%m-%Y", gmtime()))
    time_label = str(strftime("%H:%M", gmtime()))
    for o,o_label in origins:
        for d,d_label in destinations:
            url = create_url(o,d)
            server_data = get_data_from_server(url)
            data_point = {}
            data_point["origin"] = o_label
            data_point["destination"] = d_label
            data_point["commute_time"] = server_data["rows"][0]["elements"][0]["duration"]["value"]
            data_point["time"] = time_label
            data_point["date"] = date_label
            write_data_to_disk(write_path,data_point)
            time.sleep(query_timeout)

def schedule_workers(write_path):
    for q_time in query_times:
        schedule.every().day.at(q_time).do(work_unit,write_path)

def work():
    print "Starting commutr ..."
    while True:
        schedule.run_pending()
        time.sleep(scheduler_timeout) # wait one minute

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--write_file", required=True, help="Path to write file where data will be stored")
    args = vars(ap.parse_args())
    #initialize CSV file header
    with open(args["write_file"],'wb') as f:
        csv_writer = csv.DictWriter(f, empty_payload.keys())
        csv_writer.writeheader()

    schedule_workers(args["write_file"])
    work()

if __name__ == "__main__":
    main()
