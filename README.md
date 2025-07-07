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
### Instantiation and simple use
```
from soliscloud import SolisCloud


s = SolisCloud(key_id="KEY_ID", key_secret="KEY_SECRET")

status, stations = s.list_stations()

first_station = stations[0]
first_station_inverters = first_station.get_inverters()
first_station_first_inverter = first_station_inverters[0]
first_station_first_inverter_schedules first_station_first_inverter.get_charge_discharge_schedules()

```

### Charging schedules

For every inverter, there are three charging schedules.

One, two and three. Each one represents a charge and a discharge schedule.

Representation of each schedule consists of a charge start / end and current.

Just in case the schedule needs to be set on an individual inverter, the method ```set_charge_discharge_schedules``` is available on the inverter.

If you want to set the schdule at the SolisCloud level, this can be carried
out using the method ```set_inverter_charge_discharge_schedule```.

Managing schedules can be done using individual schedules or using the
same schedule across all inverters.