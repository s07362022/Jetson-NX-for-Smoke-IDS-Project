from influxdb import InfluxDBClient

import time
client = InfluxDBClient('140.128.110.57', 8086, '', '', 'env_data') 
from datetime import datetime
tem = 23.9
dry = 50.2
light = 600
gps1 = "12.123.4"
gps2 = "12.123.4"
wind = "0"


#
json_body = [
    {
        "measurement": "env",
        "tags": {
            "topic": "Sensor/env"
        },
        #"time":str(datetime.utcnow()),
        "fields": {
            "tem": tem
        }
    },
    {
        "measurement": "env",
        "tags": {
            "topic": "Sensor/env"
        },
        #"time": str(datetime.utcnow()),
        "fields": {
            "dry": dry
        }
    },
    {
        "measurement": "env",
        "tags": {
            "topic": "Sensor/env"
        },
        #"time": str(datetime.utcnow()),
        "fields": {
            "light":light
        }
    }
]
#

#DB########################################

############db############
#for i in range(15):
    #sql(tem,dry,light,gps1,gps2)
    #client.write_points(json_body)
    #time.sleep(1)
#,gps,wind)
#client.write_points(json_body)

def get_sql():
    result = client.query('select * from env') 
    insql_list=list(result.get_points())
    return insql_list
