''' Program is scheduled to run for every 4 hours. $ crontab -e has the schedule. 
Sensor pin is connected to GPIO 8 and pump pin is connected to GPIO 7
Water pump is switched ON if the moisture goes low
Watering history and program history stored in the database 
SMS sent to the mobile if watered '''

import RPi.GPIO as GPIO
import mysql.connector
from mysql.connector import Error
import time
from datetime import datetime, timezone, date

'''Below are my implemention for db and text message. 
Please use your choice of db and notification service
I am using MySql db and Twilio for text msg notifications.''' 
import dbservice as dbservice
import notification as notification

sensor_pin = 8
pump_pin = 7
watering_status = 'WATER NOT REQUIRED'

current_time = datetime.now().strftime("%B %d, %Y %H:%M:%S")

GPIO.setmode(GPIO.BOARD)

def get_status(pin):
    GPIO.setup(pin, GPIO.IN)
    return GPIO.input(pin)


def init_output(pin):
    GPIO.setup(pin, GPIO.OUT)


def start_pump(pin):
    init_output(pin)
    GPIO.output(pin,GPIO.LOW)
    time.sleep(7)
    GPIO.output(pin,GPIO.HIGH)

# check the soil moisture level
soil_moisture = get_status(sensor_pin)

mydb = dbservice.get_db_conn()
mycursor = mydb.cursor()

# If soil moisture is low ~ 1
# turn on the pump
if soil_moisture:
    start_pump(pump_pin)
    notification.send_message("Watered the plants. Time: "+current_time)
    watering_status = 'WATERED'
    insert_sql = "insert into irrigation_watering_history (moisture_status, watering_date) values ( %s, %s)"
    values = [soil_moisture, current_time]
    mycursor.execute(insert_sql,values)
    mydb.commit()


# Store the program run history
insert_sql = "insert into irrigation_program_logs (program_run_time, moisture_status, watering_status) values ( %s, %s, %s)"
values = [current_time, soil_moisture, watering_status]
mycursor.execute(insert_sql,values)
mydb.commit()
