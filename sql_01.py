###### SQL #########

from operator import imod
from influxdb import InfluxDBClient
import time
client = InfluxDBClient('140.128.110.57', 8086, '', '', 'gps_data') 
def in_sql(n,e):
    json_body = [
    {
        "measurement": "gps_id",
        "tags": {
            "topic": "Sensor/gps"
        },
        #"time":str(datetime.utcnow()),
        "fields": {
            "N": n
        }
    },
    {
        "measurement": "gps_id",
        "tags": {
            "topic": "Sensor/gps"
        },
        #"time": str(datetime.utcnow()),
        "fields": {
            "E": e
        }
    },
    
    ]
    client.write_points(json_body)
   
def get_sql():
    result = client.query('select * from gps_id') 
    insql_list=list(result.get_points())
    return insql_list
