from operator import imod
from influxdb import InfluxDBClient
import time
client = InfluxDBClient('192.168.13.22', 8086, '', '', 'smoke_ids01') #192.168.13.22 172.20.10.13
def in_sql(level_value):
    data = [
        {
            "measurement": "smoke_level",
            "tags": {
                "topic": "Sensor/level"
            },
            "fields": {
                "Level": level_value
            }
        }
    ]
    data2 = [
        {
            "measurement": "smoke_level",
            "tags": {
                "topic": "Sensor/data"
            },
            "fields": {
                "value": level_value
            }
        }
    ]
    client.write_points(data)

def get_sql():
    result = client.query('select Level from smoke_level') 
    insql_level=list(result.get_points())[-1]['Level']
    insql_time = list(result.get_points())[-1]['time']
    return insql_level,insql_time 
