# SolisCloud

A small library to work with the Solis Cloud API for some simple
data gathering and setting.

## Prerequisites

Usage of the API requires an active account on https://www.soliscloud.com and also requires an API key and secret, to be obtained via SolisCloud.

- Submit a service ticket and wait till it is resolved.
- Go to https://www.soliscloud.com/#/apiManage.
- Activate API management and agree with the usage conditions.
- After activation, click on view key tot get a pop-up window asking for the verification code.
- First click on "Verification code" after which you get an image with 2 puzzle pieces, which you need to overlap each other using the slider below.
- After that, you will receive an email with the verification code you need to enter (within 60 seconds).
- Once confirmed, you get the:
  - KEY_ID
  - KEY_SECRET
  - API URL


## Python use

```
from soliscloud import SolisCloud, SolisInverters, SolisStations


s = SolisCloud(key_id="KEY_ID", key_secret="KEY_SECRET")

stations = s.get_station_list()

first_station = stations.stations[0]
first_station_inverters = first_station.get_inverters()
first_station_first_inverter = first_station_inverters.inverters[0]

print(first_station_first_inverter.city)
```