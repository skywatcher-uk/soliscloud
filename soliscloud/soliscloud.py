from __future__ import annotations
from requests import Session
from datetime import datetime, time, date, timezone
from base64 import b64encode
from typing import Optional, Literal
import hashlib
import pytz
import hmac
import json
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_fixed


EPMFields = Literal["u_ac1","u_ac2","u_ac3","i_ac1","i_ac2","i_ac3","p_ac1","p_ac2","p_ac3","power_factor","fac_meter","p_load","e_total_inverter","e_total_load","e_total_buy","e_total_sell"]

class StatusVo():
    def __init__(self):
        self.all: int = 0
        self.normal: int = 0
        self.fault: int = 0
        self.offline: int = 0
        self.building: int = 0
        self.mppt: int = 0
    
    def _from_json(self, json_data) -> StatusVo:
        if json_data:
            for key, value in json_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        return self
    
    def _to_json(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}


class SolisConnectException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class SolisStation():
    def __init__(self, __parent__: SolisCloud = None):
        self.__parent__: SolisCloud = __parent__
        self.inverters: Optional[list[SolisInverter]] = None
        self.accessTime: int = 0
        self.accessTimeStr: str = ""
        self.addrOrigin: str = ""
        self.alarmCount: int = 0
        self.alarmLongStr: str = ""
        self.allEnergy: float = 0.0
        self.allEnergy1: float = 0.0
        self.allEnergyStr: str = ""
        self.allIncome: float = 0.0
        self.azimuth: float = 0.0
        self.batteryTodayChargeEnergy: float = 0.0
        self.batteryTodayDischargeEnergy: float = 0.0
        self.batteryTotalChargeEnergy: float = 0.0
        self.batteryTotalDischargeEnergy: float = 0.0
        self.capacity: float = 0.0
        self.capacity1: float = 0.0
        self.capacityPercent: float = 0.0
        self.capacityStr: str = ""
        self.chargerCount: int = 0
        self.city: str = ""
        self.cityStr: str = ""
        self.condCodeD: str = ""
        self.condTxtD: str = ""
        self.connectTime: int = 0
        self.connectTimeStr: str = ""
        self.country: str = ""
        self.countryStr: str = ""
        self.createDate: int = 0
        self.createDateStr: str = ""
        self.dataTimestamp: str = ""
        self.dataTimestampStr: str = ""
        self.dayEnergy: float = 0.0
        self.dayEnergy1: float = 0.0
        self.dayEnergyStr: str = ""
        self.dayIncome: float = 0.0
        self.dayPowerGeneration: float = 0.0
        self.daylight: int = 0
        self.dcInputType: int = 0
        self.dip: float = 0.0
        self.epmCount: int = 0
        self.epmType: int = 0
        self.fisGenerateTime: int = 0
        self.fisGenerateTimeStr: str = ""
        self.fisPowerTime: int = 0
        self.fisPowerTimeStr: str = ""
        self.fullHour: float = 0.0
        self.gridPurchasedTodayEnergy: float = 0.0
        self.gridPurchasedTotalEnergy: float = 0.0
        self.gridSellTodayEnergy: float = 0.0
        self.gridSellTotalEnergy: float = 0.0
        self.gridSwitch: int = 0
        self.gridSwitch1: int = 0
        self.groupId: str = ""
        self.homeLoadTodayEnergy: float = 0.0
        self.homeLoadTotalEnergy: float = 0.0
        self.id: str = ""
        self.installer: str = ""
        self.inverterCount: int = 0
        self.inverterOnlineCount: int = 0
        self.inverterStateOrder: int = 0
        self.jxbType: int = 0
        self.module: str = ""
        self.money: str = ""
        self.monthCarbonDioxide: float = 0.0
        self.monthEnergy: float = 0.0
        self.monthEnergy1: float = 0.0
        self.monthEnergyStr: str = ""
        self.oneSelf: float = 0.0
        self.oneSelfTotal: float = 0.0
        self.pic1Url: str = ""
        self.picName: str = ""
        self.power: float = 0.0
        self.power1: float = 0.0
        self.powerStr: str = ""
        self.price: float = 0.0
        self.region: str = ""
        self.regionStr: str = ""
        self.shareProcess: int = 0
        self.simFlowState: int = 0
        self.sno: str = ""
        self.state: int = 0
        self.stationName: str = ""
        self.stationTypeNew: int = 0
        self.synchronizationType: int = 0
        self.timeZone: float = 0.0
        self.timeZoneId: str = ""
        self.timeZoneName: str = ""
        self.timeZoneStr: str = ""
        self.type: int = 0
        self.updateDate: int = 0
        self.userId: str = ""
        self.yearEnergy: float = 0.0
        self.yearEnergy1: float = 0.0
        self.yearEnergyStr: str = ""

    def _from_json(self, json_data) -> SolisStation:
        for key, value in json_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
    
    def _to_json(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}
    
    def list_inverters(self) -> list[SolisInverter]:
        if self.__parent__:
            self.inverters = self.__parent__.list_inverters(stationId=self.id)
            return self.inverters


class EPMDataDayItem():
    def __init__(self):
        self.alarm_count: int = 0
        self.current_state: int = 0
        self.datetime: datetime
        self.e_total_buy: float = 0.0
        self.e_total_inverter: float = 0.0
        self.e_total_load: float = 0.0
        self.e_total_sell: float = 0.0
        self.fac_meter: float = 0.0
        self.fault_bit: int = 0
        self.i_ac1: float = 0.0
        self.i_ac2: float = 0.0
        self.i_ac3: float = 0.0
        self.is_relatime: float = 0.0
        self.p_ac1: float = 0.0
        self.p_ac2: float = 0.0
        self.p_ac3: float = 0.0
        self.power_factor: int = 0
        self.u_ac1: float = 0.0
        self.u_ac2: float = 0.0
        self.u_ac3: float = 0.0
        self.state: int = 0
    
    def _to_json_(self) -> dict:
        json_obj = {}
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                json_obj[k] = v
        return json_obj
    
    def _from_json_(self, json_obj: dict) -> EPMDataDayItem:
        if isinstance(json_obj, dict):
            for k, v in json_obj.items():
                if hasattr(self, k):
                    setattr(self, k, v)
        return self


class EPMDataMonthYearItem:
    def __init__(self):
        self.backUpEnergy: int = 0
        self.consumeEnergy: int = 0
        self.date: int = 0
        self.datetime: datetime = None
        self.dateStr: str = ""
        self.directR: int = 0
        self.directRKwh: int = 0
        self.energy: float = 0.0
        self.energyPec: str = ""
        self.energyStr: str = ""
        self.epmBuyEnergy: float = 0.0
        self.epmLoadEnergy: float = 0.0
        self.epmSellEnergy: float = 0.0
        self.errorFlag: int = 0
        self.generatorEnergy: float = 0.0
        self.generatorPercent: float = 0.0
        self.gridBatteryE: int = 0
        self.gridPurchasedEnergy: int = 0
        self.gridPurchasedIncome: float = 0.0
        self.gridPurchasedPercent: float = 0.0
        self.gridSellEnergy: int = 0
        self.gridSellIncome: float = 0.0
        self.homeGridEnergy: int = 0
        self.id: str = ""
        self.invAcE: int = 0
        self.money: float = 0.0
        self.oneSelfPercent: float = 0.0
        self.produceEnergy: int = 0
        self.systemEfficiency: int = 0
        self.timeZone: int = 0
        self.toConsumption: int = 0
        self.toGrid: int = 0
        self.totalR: int = 0
        self.totalRKwh: int = 0

    def _from_json_(self, json_obj: dict):
        for key in json_obj:
            if hasattr(self, key):
                setattr(self, key, json_obj[key])
            if key == "date":
                self.datetime = datetime.fromtimestamp(int(json_obj[key]) / 1000)

    def _to_json_(self) -> dict:
        json_obj = {}
        for k, v in self.__dict__.items():
            if k == "datetime":
                continue
            if not k.startswith("_"):
                json_obj[k] = v
        return json_obj


class EPMDayData():
    def __init__(self):
        self.formatted_data: list[EPMDataDayItem] = []

    def _from_json_(self, json_data: dict) -> EPMDayData:
        if json_data:
            keys = [x for x in json_data.keys()]
            if "data_timestamp" in keys:
                data_timestamp = json_data.get('data_timestamp', [])
                keys.remove('data_timestamp')                
                for x in range(0, len(data_timestamp)):
                    try:
                        dt_dt = datetime.fromtimestamp(int(data_timestamp[x])/ 1000)
                        epm = EPMDataDayItem()
                        epm.datetime = dt_dt
                        for key in keys:
                            if hasattr(epm, key):
                                setattr(epm, key, json_data[key][x])
                        self.formatted_data.append(epm)
                    except Exception as err:
                        pass
        return self
    
    def convert_to_json(self) -> dict:
        json_obj = {}
        for item in self.formatted_data:
            json_obj[item.datetime.isoformat()] = item._to_json_()
        return dict(sorted(json_obj.items()))


class EPMMonthYearData():
    def __init__(self):
        self.formatted_data: list[EPMDataMonthYearItem] = []

    def _from_json_(self, json_data: dict) -> EPMMonthYearData:
        if json_data:
            for item in json_data:
                epm = EPMDataMonthYearItem()
                epm._from_json_(item)
                self.formatted_data.append(epm)
        return self
    
    def convert_to_json(self) -> dict:
        json_obj = {}
        for item in self.formatted_data:
            json_obj[item.datetime.isoformat()] = item._to_json_()
        return dict(sorted(json_obj.items()))


class SolisEPM():
    collectorId: str
    collectorSn: str
    ctRatio: float
    currentState: str
    dataTimestamp: str
    daylight: int
    eToaalInverter: str
    eToaalInverterOrigin: float
    eToaalInverterStr: float
    eTodayBuy: 0
    eTodayBuyOrigin: 0
    eTodayBuyStr: str
    eTodaySell: str
    eTodaySellOrigin: str
    eTodaySellStr: str
    eTotalBuy: str
    eTotalBuyOrigin: str
    eTotalBuyStr: str
    eTotalLoad: str
    eTotalLoadOrigin: str
    eTotalLoadStr: str
    eTotalSell: str
    eTotalSellOrigin: str
    eTotalSellStr: str
    empSoftwareVersion: str
    epmDataTime: str
    epmModel: str
    epmMonthLoadEnergy: str
    epmMonthLoadEnergyOrigin: str
    epmMonthLoadEnergyStr: str
    epmTodayLoadEnergy: str
    epmTodayLoadEnergyOrigin: str
    epmTodayLoadEnergyStr: str
    epmTotalLoadEnergy: str
    epmTotalLoadEnergyOrigin: str
    epmTotalLoadEnergyStr: str
    epmType: str
    facMeter: str
    failSafe: str
    g100v2State: str
    gridSwitch1: str
    iAc1: str
    iAc1Str: str
    iAc2: str
    iAc2Str: str
    iAc3: str
    iAc3Str: str
    id: str
    inverterModel: str
    inverterNum: str
    isRealtime: str
    monthBuy: str
    monthBuyOrigin: str
    monthBuyStr: str
    monthSell: str
    monthSellOrigin: str
    monthSellStr: str
    pAc1: str
    pAc1Str: str
    pAc2: str
    pAc2Str: str
    pAc3: str
    pAc3Str: str
    pEpmTotal: str
    pEpmTotalOrigin: str
    pEpmTotalPec: str
    pEpmTotalStr: str
    pInverterTotal: str
    pInverterTotalOrigin: str
    pInverterTotalStr: str
    pLimit: str
    pLoad: str
    pLoadOrigin: str
    pLoadStr: str
    pSet: str
    pSetOrigin: str
    pSetStr: str
    powerFactor: str
    rs485ComAddr: str
    sn: str
    sno: str
    state: str
    stateExceptionFlag: str
    stationId: str
    stationName: str
    stationType: str
    stationTypeNew: str
    synchronizationType: str
    tag: str
    timeZone: str
    timeZoneStr: str
    uAc1: str
    uAc1Str: str
    uAc2: str
    uAc2Str: str
    uAc3: str
    uAc3Str: str
    userId: str
    def __init__(self, __parent__: SolisCloud):
        self.__parent__: SolisCloud = __parent__
        self.collectorId = ""
        self.collectorSn = ""
        self.ctRatio = 0.0
        self.currentState = ""
        self.dataTimestamp = ""
        self.daylight = 0
        self.eToaalInverter = 0.0
        self.eToaalInverterOrigin = 0.0
        self.eToaalInverterStr = ""
        self.eTodayBuy = 0
        self.eTodayBuyOrigin = 0
        self.eTodayBuyStr = ""
        self.eTodaySell = ""
        self.eTodaySellOrigin = ""
        self.eTodaySellStr = ""
        self.eTotalBuy = ""
        self.eTotalBuyOrigin = ""
        self.eTotalBuyStr = ""
        self.eTotalLoad = ""
        self.eTotalLoadOrigin = ""
        self.eTotalLoadStr = ""
        self.eTotalSell = ""
        self.eTotalSellOrigin = ""
        self.eTotalSellStr = ""
        self.empSoftwareVersion = ""
        self.epmDataTime = ""
        self.epmModel = ""
        self.epmMonthLoadEnergy = ""
        self.epmMonthLoadEnergyOrigin = ""
        self.epmMonthLoadEnergyStr = ""
        self.epmTodayLoadEnergy = ""
        self.epmTodayLoadEnergyOrigin = ""
        self.epmTodayLoadEnergyStr = ""
        self.epmTotalLoadEnergy = ""
        self.epmTotalLoadEnergyOrigin = ""
        self.epmTotalLoadEnergyStr = ""
        self.epmType = ""
        self.facMeter = ""
        self.failSafe = ""
        self.g100v2State = ""
        self.gridSwitch1 = ""
        self.iAc1 = ""
        self.iAc1Str = ""
        self.iAc2 = ""
        self.iAc2Str = ""
        self.iAc3 = ""
        self.iAc3Str = ""
        self.id = ""
        self.inverterModel = ""
        self.inverterNum = ""
        self.isRealtime = ""
        self.monthBuy = ""
        self.monthBuyOrigin = ""
        self.monthBuyStr = ""
        self.monthSell = ""
        self.monthSellOrigin = ""
        self.monthSellStr = ""
        self.pAc1 = ""
        self.pAc1Str = ""
        self.pAc2 = ""
        self.pAc2Str = ""
        self.pAc3 = ""
        self.pAc3Str = ""
        self.pEpmTotal = ""
        self.pEpmTotalOrigin = ""
        self.pEpmTotalPec = ""
        self.pEpmTotalStr = ""
        self.pInverterTotal = ""
        self.pInverterTotalOrigin = ""
        self.pInverterTotalStr = ""
        self.pLimit = ""
        self.pLoad = ""
        self.pLoadOrigin = ""
        self.pLoadStr = ""
        self.pSet = ""
        self.pSetOrigin = ""
        self.pSetStr = ""
        self.powerFactor = ""
        self.rs485ComAddr = ""
        self.sn = ""
        self.sno = ""
        self.state = ""
        self.stateExceptionFlag = ""
        self.stationId = ""
        self.stationName = ""
        self.stationType = ""
        self.stationTypeNew = ""
        self.synchronizationType = ""
        self.tag = ""
        self.timeZone = ""
        self.timeZoneStr = ""
        self.uAc1 = ""
        self.uAc1Str = ""
        self.uAc2 = ""
        self.uAc2Str = ""
        self.uAc3 = ""
        self.uAc3Str = ""
        self.userId = ""
    
    def get_data_for_day(self, dt: date, timeZone: int, searchinfo: list[EPMFields] = [], **kwargs) -> EPMDayData:
        data: EPMDayData = self.__parent__.get_epm_data_for_day(sn=self.sn, dt=dt, timeZone=timeZone, searchinfo=searchinfo, **kwargs)
        return data
    
    def get_data_for_month(self, dt: date, **kwargs) -> EPMMonthYearData:
        data: EPMMonthYearData = self.__parent__.get_epm_data_for_month(sn=self.sn, dt=dt, **kwargs)
        return data
    
    def get_data_for_year(self, dt: date, **kwargs) -> EPMMonthYearData:
        data: EPMMonthYearData = self.__parent__.get_epm_data_for_year(sn=self.sn, dt=dt, **kwargs)
        return data

    def _to_json(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}
        
    def _from_json(self, json_data) -> SolisEPM:
        if json_data:
            for key, value in json_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        return self


class SolisStations():
    def __init__(self):
        self.stationStatusVo: StatusVo = StatusVo()
        self.stations: list[SolisStation] = []
    
    def _from_json(self, json_data) -> SolisStations:
        for key, value in json_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
    
    def _to_json(self) -> dict:
        json_obj = {}
        json_obj['stationsStatusVo'] = self.stationStatusVo._to_json()
        json_obj['stations'] = [x._to_json() for x in self.stations]
        return json_obj


class SolisInverter():
    def __init__(self, __parent__: SolisCloud = None):
        self.__parent__: SolisCloud = __parent__
        self.charge_discharge_schedule: ChargeDischargeSchedule = None
        self.chartAllParams: str = ''
        self.id: str = ''
        self.userId: str = ''
        self.sn: str = ''
        self.inverterMeterModel: int = 0
        self.collectorsn: str = ''
        self.collectorId: str = ''
        self.state: int = 0
        self.stateExceptionFlag: int = 0
        self.mpptSwitch: int = 0
        self.collectorState: int = 0
        self.collectorModel: str = ''
        self.simFlowState: int = 0
        self.ammeterId: str = ''
        self.electricMeter: int = 0
        self.fullHour: float = 0.0
        self.fullHourStr: str = ''
        self.currentState: str = ''
        self.alarmState: int = 0
        self.warningInfoData: int = 0
        self.shelfBeginTime: int = 0
        self.shelfEndTime: int = 0
        self.updateShelfEndTime: int = 0
        self.updateShelfEndTimeStr: str = ''
        self.shelfState: str = ''
        self.timeZone: float = 0.0
        self.timeZoneStr: str = ''
        self.daylight: int = 0
        self.daylightSwitch: int = 0
        self.model: str = ''
        self.productModel: str = ''
        self.isS5: int = 0
        self.isSeparateLoad: int = 0
        self.isShowPowerFactor: int = 0
        self.isShowInternalBatteryI: int = 0
        self.ctrlCommand: int = 0
        self.inverterType: int = 0
        self.nationalStandards: str = ''
        self.nationalStandardstr: str = ''
        self.inverterTemperature: float = 0.0
        self.inverterTemperatureUnit: str = ''
        self.inverterTemperature2: float = 0.0
        self.inverterTemperatureUnit2: str = ''
        self.temp: float = 0.0
        self.tempName: str = ''
        self.stationName: str = ''
        self.stationType: int = 0
        self.stationTypeNew: int = 0
        self.epmType: int = 0
        self.synchronizationType: int = 0
        self.gridSwitch1: int = 0
        self.sno: str = ''
        self.money: str = ''
        self.stationId: str = ''
        self.version: str = ''
        self.version2: str = ''
        self.acOutputType: int = 0
        self.dcInputtype: int = 0
        self.rs485ComAddr: str = ''
        self.dataTimestamp: str = ''
        self.timeStr: str = ''
        self.tag: str = ''
        self.reactivePower: float = 0.0
        self.apparentPower: float = 0.0
        self.dcPac: float = 0.0
        self.uInitGnd: int = 0
        self.uInitGndStr: str = ''
        self.dcBus: float = 0.0
        self.dcBusStr: str = ''
        self.dcBusHalf: float = 0.0
        self.dcBusHalfStr: str = ''
        self.power: float = 0.0
        self.powerStr: str = ''
        self.powerPec: str = ''
        self.porwerPercent: float = 0.0
        self.pac: float = 0.0
        self.pacStr: str = ''
        self.pacPec: str = ''
        self.oneSelf: float = 0.0
        self.eToday: float = 0.0
        self.eTodayStr: str = ''
        self.eMonth: float = 0.0
        self.eMonthStr: str = ''
        self.eYear: float = 0.0
        self.eYearStr: str = ''
        self.eTotal: float = 0.0
        self.eTotalStr: str = ''
        self.dayInCome: float = 0.0
        self.monthInCome: float = 0.0
        self.yearInCome: float = 0.0
        self.allInCome: float = 0.0
        self.uPv1: int = 0
        self.uPv1Str: str = ''
        self.iPv1: int = 0
        self.iPv1Str: str = ''
        self.uPv2: int = 0
        self.uPv2Str: str = ''
        self.iPv2: int = 0
        self.iPv2Str: str = ''
        self.uPv3: int = 0
        self.uPv3Str: str = ''
        self.iPv3: int = 0
        self.iPv3Str: str = ''
        self.uPv4: int = 0
        self.uPv4Str: str = ''
        self.iPv4: int = 0
        self.iPv4Str: str = ''
        self.uPv5: int = 0
        self.uPv5Str: str = ''
        self.iPv5: int = 0
        self.iPv5Str: str = ''
        self.uPv6: int = 0
        self.uPv6Str: str = ''
        self.iPv6: int = 0
        self.iPv6Str: str = ''
        self.uPv7: int = 0
        self.uPv7Str: str = ''
        self.iPv7: int = 0
        self.iPv7Str: str = ''
        self.uPv8: int = 0
        self.uPv8Str: str = ''
        self.iPv8: int = 0
        self.iPv8Str: str = ''
        self.uPv9: int = 0
        self.uPv9Str: str = ''
        self.iPv9: int = 0
        self.iPv9Str: str = ''
        self.uPv10: int = 0
        self.uPv10Str: str = ''
        self.iPv10: int = 0
        self.iPv10Str: str = ''
        self.uPv11: int = 0
        self.uPv11Str: str = ''
        self.iPv11: int = 0
        self.iPv11Str: str = ''
        self.uPv12: int = 0
        self.uPv12Str: str = ''
        self.iPv12: int = 0
        self.iPv12Str: str = ''
        self.uPv13: int = 0
        self.uPv13Str: str = ''
        self.iPv13: int = 0
        self.iPv13Str: str = ''
        self.uPv14: int = 0
        self.uPv14Str: str = ''
        self.iPv14: int = 0
        self.iPv14Str: str = ''
        self.uPv15: int = 0
        self.uPv15Str: str = ''
        self.iPv15: int = 0
        self.iPv15Str: str = ''
        self.uPv16: int = 0
        self.uPv16Str: str = ''
        self.iPv16: int = 0
        self.iPv16Str: str = ''
        self.uPv17: int = 0
        self.uPv17Str: str = ''
        self.iPv17: int = 0
        self.iPv17Str: str = ''
        self.uPv18: int = 0
        self.uPv18Str: str = ''
        self.iPv18: int = 0
        self.iPv18Str: str = ''
        self.uPv19: int = 0
        self.uPv19Str: str = ''
        self.iPv19: int = 0
        self.iPv19Str: str = ''
        self.uPv20: int = 0
        self.uPv20Str: str = ''
        self.iPv20: int = 0
        self.iPv20Str: str = ''
        self.uPv21: int = 0
        self.uPv21Str: str = ''
        self.iPv21: int = 0
        self.iPv21Str: str = ''
        self.uPv22: int = 0
        self.uPv22Str: str = ''
        self.iPv22: int = 0
        self.iPv22Str: str = ''
        self.uPv23: int = 0
        self.uPv23Str: str = ''
        self.iPv23: int = 0
        self.iPv23Str: str = ''
        self.uPv24: int = 0
        self.uPv24Str: str = ''
        self.iPv24: int = 0
        self.iPv24Str: str = ''
        self.uPv25: int = 0
        self.uPv25Str: str = ''
        self.iPv25: int = 0
        self.iPv25Str: str = ''
        self.uPv26: int = 0
        self.uPv26Str: str = ''
        self.iPv26: int = 0
        self.iPv26Str: str = ''
        self.uPv27: int = 0
        self.uPv27Str: str = ''
        self.iPv27: int = 0
        self.iPv27Str: str = ''
        self.uPv28: int = 0
        self.uPv28Str: str = ''
        self.iPv28: int = 0
        self.iPv28Str: str = ''
        self.uPv29: int = 0
        self.uPv29Str: str = ''
        self.iPv29: int = 0
        self.iPv29Str: str = ''
        self.uPv30: int = 0
        self.uPv30Str: str = ''
        self.iPv30: int = 0
        self.iPv30Str: str = ''
        self.uPv31: int = 0
        self.uPv31Str: str = ''
        self.iPv31: int = 0
        self.iPv31Str: str = ''
        self.uPv32: int = 0
        self.uPv32Str: str = ''
        self.iPv32: int = 0
        self.iPv32Str: str = ''
        self.pow1: int = 0
        self.pow1Str: str = ''
        self.pow2: int = 0
        self.pow2Str: str = ''
        self.pow3: int = 0
        self.pow3Str: str = ''
        self.pow4: int = 0
        self.pow4Str: str = ''
        self.pow5: int = 0
        self.pow5Str: str = ''
        self.pow6: int = 0
        self.pow6Str: str = ''
        self.pow7: int = 0
        self.pow7Str: str = ''
        self.pow8: int = 0
        self.pow8Str: str = ''
        self.pow9: int = 0
        self.pow9Str: str = ''
        self.pow10: int = 0
        self.pow10Str: str = ''
        self.pow11: int = 0
        self.pow11Str: str = ''
        self.pow12: int = 0
        self.pow12Str: str = ''
        self.pow13: int = 0
        self.pow13Str: str = ''
        self.pow14: int = 0
        self.pow14Str: str = ''
        self.pow15: int = 0
        self.pow15Str: str = ''
        self.pow16: int = 0
        self.pow16Str: str = ''
        self.pow17: int = 0
        self.pow17Str: str = ''
        self.pow18: int = 0
        self.pow18Str: str = ''
        self.pow19: int = 0
        self.pow19Str: str = ''
        self.pow20: int = 0
        self.pow20Str: str = ''
        self.pow21: int = 0
        self.pow21Str: str = ''
        self.pow22: int = 0
        self.pow22Str: str = ''
        self.pow23: int = 0
        self.pow23Str: str = ''
        self.pow24: int = 0
        self.pow24Str: str = ''
        self.pow25: int = 0
        self.pow25Str: str = ''
        self.pow26: int = 0
        self.pow26Str: str = ''
        self.pow27: int = 0
        self.pow27Str: str = ''
        self.pow28: int = 0
        self.pow28Str: str = ''
        self.pow29: int = 0
        self.pow29Str: str = ''
        self.pow30: int = 0
        self.pow30Str: str = ''
        self.pow31: int = 0
        self.pow31Str: str = ''
        self.pow32: int = 0
        self.pow32Str: str = ''
        self.uAc1: float = 0.0
        self.uAc1Str: str = ''
        self.iAc1: float = 0.0
        self.iAc1Str: str = ''
        self.uAc2: float = 0.0
        self.uAc2Str: str = ''
        self.iAc2: float = 0.0
        self.iAc2Str: str = ''
        self.uAc3: float = 0.0
        self.uAc3Str: str = ''
        self.iAc3: float = 0.0
        self.iAc3Str: str = ''
        self.powerFactor: float = 0.0
        self.batteryDischargeEnergy: float = 0.0
        self.batteryDischargeEnergyStr: str = ''
        self.batteryChargeEnergy: float = 0.0
        self.batteryChargeEnergyStr: str = ''
        self.homeLoadEnergy: float = 0.0
        self.homeLoadEnergyStr: str = ''
        self.gridPurchasedEnergy: float = 0.0
        self.gridPurchasedEnergyStr: str = ''
        self.gridSellEnergy: float = 0.0
        self.gridSellEnergyStr: str = ''
        self.fac: float = 0.0
        self.facStr: str = ''
        self.batteryPower: float = 0.0
        self.batteryPowerStr: str = ''
        self.batteryPowerPec: str = ''
        self.batteryPowerZheng: int = 0
        self.batteryPowerFu: float = 0.0
        self.storageBatteryVoltage: float = 0.0
        self.storageBatteryVoltageStr: str = ''
        self.storageBatteryCurrent: float = 0.0
        self.storageBatteryCurrentStr: str = ''
        self.batteryCapacitySoc: float = 0.0
        self.batteryHealthSoh: float = 0.0
        self.batteryVoltage: float = 0.0
        self.batteryVoltageStr: str = ''
        self.bstteryCurrent: float = 0.0
        self.bstteryCurrentStr: str = ''
        self.batteryPowerBms: float = 0.0
        self.batteryPowerBmsStr: str = ''
        self.internalBatteryI: float = 0.0
        self.batteryChargingCurrent: float = 0.0
        self.batteryChargingCurrentStr: str = ''
        self.batteryDischargeLimiting: float = 0.0
        self.batteryDischargeLimitingStr: str = ''
        self.batteryFailureInformation01: str = ''
        self.batteryFailureInformation02: str = ''
        self.batteryTotalChargeEnergy: float = 0.0
        self.batteryTotalChargeEnergyStr: str = ''
        self.batteryTodayChargeEnergy: float = 0.0
        self.batteryTodayChargeEnergyStr: str = ''
        self.batteryMonthChargeEnergy: float = 0.0
        self.batteryMonthChargeEnergyStr: str = ''
        self.batteryYearChargeEnergy: float = 0.0
        self.batteryYearChargeEnergyStr: str = ''
        self.batteryYesterdayChargeEnergy: float = 0.0
        self.batteryYesterdayChargeEnergyStr: str = ''
        self.batteryTotalDischargeEnergy: float = 0.0
        self.batteryTotalDischargeEnergyStr: str = ''
        self.batteryTodayDischargeEnergy: float = 0.0
        self.batteryTodayDischargeEnergyStr: str = ''
        self.batteryMonthDischargeEnergy: float = 0.0
        self.batteryMonthDischargeEnergyStr: str = ''
        self.batteryYearDischargeEnergy: float = 0.0
        self.batteryYearDischargeEnergyStr: str = ''
        self.batteryYesterdayDischargeEnergy: float = 0.0
        self.batteryYesterdayDischargeEnergyStr: str = ''
        self.gridPurchasedTotalEnergy: float = 0.0
        self.gridPurchasedTotalEnergyStr: str = ''
        self.gridPurchasedYearEnergy: float = 0.0
        self.gridPurchasedYearEnergyStr: str = ''
        self.gridPurchasedMonthEnergy: float = 0.0
        self.gridPurchasedMonthEnergyStr: str = ''
        self.gridPurchasedTodayEnergy: float = 0.0
        self.gridPurchasedTodayEnergyStr: str = ''
        self.gridPurchasedYesterdayEnergy: float = 0.0
        self.gridPurchasedYesterdayEnergyStr: str = ''
        self.gridSellTotalEnergy: float = 0.0
        self.gridSellTotalEnergyStr: str = ''
        self.gridSellYearEnergy: float = 0.0
        self.gridSellYearEnergyStr: str = ''
        self.gridSellMonthEnergy: float = 0.0
        self.gridSellMonthEnergyStr: str = ''
        self.gridSellTodayEnergy: float = 0.0
        self.gridSellTodayEnergyStr: str = ''
        self.gridSellYesterdayEnergy: float = 0.0
        self.gridSellYesterdayEnergyStr: str = ''
        self.homeLoadTodayEnergy: float = 0.0
        self.homeLoadTodayEnergyStr: str = ''
        self.homeLoadMonthEnergy: float = 0.0
        self.homeLoadMonthEnergyStr: str = ''
        self.homeLoadYearEnergy: float = 0.0
        self.homeLoadYearEnergyStr: str = ''
        self.homeLoadTotalEnergy: float = 0.0
        self.homeLoadTotalEnergyStr: str = ''
        self.totalLoadPower: float = 0.0
        self.totalLoadPowerStr: str = ''
        self.homeLoadYesterdayEnergy: float = 0.0
        self.homeLoadYesterdayEnergyStr: str = ''
        self.familyLoadPower: float = 0.0
        self.familyLoadPowerStr: str = ''
        self.familyLoadPercent: float = 0.0
        self.homeGridYesterdayEnergy: float = 0.0
        self.homeGridYesterdayEnergyStr: str = ''
        self.homeGridTodayEnergy: float = 0.0
        self.homeGridTodayEnergyStr: str = ''
        self.homeGridMonthEnergy: float = 0.0
        self.homeGridMonthEnergyStr: str = ''
        self.homeGridYearEnergy: float = 0.0
        self.homeGridYearEnergyStr: str = ''
        self.homeGridTotalEnergy: float = 0.0
        self.homeGridTotalEnergyStr: str = ''
        self.bypassLoadPower: float = 0.0
        self.bypassLoadPowerStr: str = ''
        self.backupYesterdayEnergy: float = 0.0
        self.backupYesterdayEnergyStr: str = ''
        self.backupTodayEnergy: float = 0.0
        self.backupTodayEnergyStr: str = ''
        self.backupMonthEnergy: float = 0.0
        self.backupMonthEnergyStr: str = ''
        self.backupYearEnergy: float = 0.0
        self.backupYearEnergyStr: str = ''
        self.backupTotalEnergy: float = 0.0
        self.backupTotalEnergyStr: str = ''
        self.bypassAcVoltage: float = 0.0
        self.bypassAcVoltageB: float = 0.0
        self.bypassAcVoltageC: float = 0.0
        self.bypassAcCurrent: float = 0.0
        self.bypassAcCurrentB: float = 0.0
        self.bypassAcCurrentC: float = 0.0
        self.pLimitSet: float = 0.0
        self.pFactorLimitSet: float = 0.0
        self.pReactiveLimitSet: float = 0.0
        self.batteryType: str = ''
        self.batteryTypeCode: str = ''
        self.batteryModel: int = 0
        self.socDischargeSet: float = 0.0
        self.socChargingSet: float = 0.0
        self.pEpmSet: float = 0.0
        self.pEpmSetStr: str = ''
        self.epmFailSafe: float = 0.0
        self.epmSafe: int = 0
        self.pEpm: float = 0.0
        self.pEpmStr: str = ''
        self.psumCalPec: str = ''
        self.insulationResistance: float = 0.0
        self.dispersionRate: float = 0.0
        self.sirRealtime: int = 0
        self.iLeakLimt: int = 0
        self.upvTotal: int = 0
        self.upvTotalStr: str = ''
        self.ipvTotal: int = 0
        self.ipvTotalStr: str = ''
        self.powTotal: int = 0
        self.powTotalStr: str = ''
        self.parallelStatus: int = 0
        self.parallelAddr: int = 0
        self.parallelPhase: int = 0
        self.parallelBattery: int = 0
        self.batteryAlarm: str = ''
        self.bypassAcOnoffSet: float = 0.0
        self.bypassAcVoltageSet: float = 0.0
        self.bypassAcCurrentSet: float = 0.0
        self.batteryCDEnableSet: float = 0.0
        self.batteryCDSet: float = 0.0
        self.batteryCDISet: float = 0.0
        self.batteryCMaxiSet: float = 0.0
        self.batteryDMaxiSet: float = 0.0
        self.batteryUvpSet: float = 0.0
        self.batteryFcvSet: float = 0.0
        self.batteryAcvSet: float = 0.0
        self.batteryOvpSet: float = 0.0
        self.batteryOlvEnableSet: float = 0.0
        self.batteryLaTemp: float = 0.0
        self.offGridDDepth: float = 0.0
        self.epsDDepth: float = 0.0
        self.epsSwitchTime: str = ''
        self.groupId: str = ''
        self.isGrouped: int = 0
        self.bmsState: int = 0
        self.isShow: bool = False
        self.isShowBattery: int = 0
        self.acInType: int = 0
        self.energyStorageControl: str = ''
        self.dsp14Ver: str = ''
        self.meter1Type: int = 0
        self.meter2Type: int = 0
        self.meter1SiteHigh: int = 0
        self.meter2SiteHigh: int = 0
        self.meter1TypeLow: int = 0
        self.meter2TypeLow: int = 0
        self.generatorPower: float = 0.0
        self.generatorPowerStr: str = ''
        self.generatorPowerPec: str = ''
        self.generatorTodayEnergy: float = 0.0
        self.generatorTodayEnergyStr: str = ''
        self.generatorTodayEnergyPec: str = ''
        self.generatorMonthEnergy: float = 0.0
        self.generatorMonthEnergyStr: str = ''
        self.generatorMonthEnergyPec: str = ''
        self.generatorYearEnergy: float = 0.0
        self.generatorYearEnergyStr: str = ''
        self.generatorYearEnergyPec: str = ''
        self.generatorTotalEnergy: float = 0.0
        self.generatorTotalEnergyStr: str = ''
        self.generatorTotalEnergyPec: str = ''
        self.generatorWarning: str = ''
        self.generatorWarningMsg: str = ''
        self.generatorSet: str = ''
        self.generatorSet01: float = 0.0
        self.parallelOnoff: str = ''
        self.parallelOnoff01: float = 0.0
        self.parallelOnoff02: float = 0.0
        self.parallelNumber: float = 0.0
        self.parallelOnline: float = 0.0
        self.tempFlag: int = 0
        self.iA: float = 0.0
        self.uA: float = 0.0
        self.pA: float = 0.0
        self.iB: float = 0.0
        self.uB: float = 0.0
        self.pB: float = 0.0
        self.iC: float = 0.0
        self.uC: float = 0.0
        self.pC: float = 0.0
        self.aReactivePower: float = 0.0
        self.aLookedPower: float = 0.0
        self.aPhasePowerFactor: float = 0.0
        self.bReactivePower: float = 0.0
        self.bLookedPower: float = 0.0
        self.bPhasePowerFactor: float = 0.0
        self.cReactivePower: float = 0.0
        self.cLookedPower: float = 0.0
        self.cPhasePowerFactor: float = 0.0
        self.averagePowerFactor: float = 0.0
        self.pvShow: int = 0
        self.mpptShow: int = 0
        self.mpptIpv1: int = 0
        self.mpptUpv1: int = 0
        self.mpptPow1: int = 0
        self.mpptIpv2: int = 0
        self.mpptUpv2: int = 0
        self.mpptPow2: int = 0
        self.mpptIpv3: int = 0
        self.mpptUpv3: int = 0
        self.mpptPow3: int = 0
        self.mpptIpv4: int = 0
        self.mpptPow4: int = 0
        self.mpptUpv4: int = 0
        self.mpptIpv5: int = 0
        self.mpptUpv5: int = 0
        self.mpptPow5: int = 0
        self.mpptIpv6: int = 0
        self.mpptUpv6: int = 0
        self.mpptPow6: int = 0
        self.mpptIpv7: int = 0
        self.mpptUpv7: int = 0
        self.mpptPow7: int = 0
        self.mpptIpv8: int = 0
        self.mpptUpv8: int = 0
        self.mpptPow8: int = 0
        self.mpptIpv9: int = 0
        self.mpptUpv9: int = 0
        self.mpptPow9: int = 0
        self.mpptIpv10: int = 0
        self.mpptUpv10: int = 0
        self.mpptPow10: int = 0
        self.mpptIpv11: int = 0
        self.mpptUpv11: int = 0
        self.mpptPow11: int = 0
        self.mpptIpv12: int = 0
        self.mpptUpv12: int = 0
        self.mpptPow12: int = 0
        self.mpptIpv13: int = 0
        self.mpptUpv13: int = 0
        self.mpptPow13: int = 0
        self.mpptIpv14: int = 0
        self.mpptUpv14: int = 0
        self.mpptPow14: int = 0
        self.mpptIpv15: int = 0
        self.mpptUpv15: int = 0
        self.mpptPow15: int = 0
        self.mpptIpv16: int = 0
        self.mpptUpv16: int = 0
        self.mpptPow16: int = 0
        self.mpptIpv17: int = 0
        self.mpptUpv17: int = 0
        self.mpptPow17: int = 0
        self.mpptIpv18: int = 0
        self.mpptUpv18: int = 0
        self.mpptPow18: int = 0
        self.mpptIpv19: int = 0
        self.mpptUpv19: int = 0
        self.mpptPow19: int = 0
        self.mpptIpv20: int = 0
        self.mpptUpv20: int = 0
        self.mpptPow20: int = 0
        self.dcInputTypeMppt: int = 0
        self.afciType: str = ''
        self.afciTypeStr: str = ''
        self.afciVer: str = ''
        self.fisTimeStr: str = ''
        self.fisGenerateTime: int = 0
        self.fisGenerateTimeStr: str = ''
        self.outDateStr: str = ''
        self.g100v2State: int = 0
        self.faultCodeDesc: str = ''
        self.machine: str = ''
        self.batteryState: int = 0
        self.sphSet: int = 0
        self.sphSn: str = ''
        self.dcAcPower: float = 0.0
        self.backupLookedPower: float = 0.0
        self.backupLookedPowerStr: str = ''
        self.backupLookedPowerOriginal: float = 0.0
        self.backupLookedPowerA: float = 0.0
        self.backupLookedPowerB: float = 0.0
        self.backupLookedPowerC: float = 0.0
        self.batteryNum: int = 0
        self.batteryType2: int = 0
        self.batteryList: list = []
        self.hmilcdVer: str = ''
        self.afciDataFlag: int = 0
        self.backup2Power: float = 0.0
        self.backup2PowerStr: str = ''
        self.backup2PowerA: float = 0.0
        self.backup2PowerB: float = 0.0
        self.backup2PowerC: float = 0.0
        self.backup2LookedPower: float = 0.0
        self.backup2LookedPowerStr: str = ''
        self.backup2LookedPowerOriginal: float = 0.0
        self.backup2LookedPowerA: float = 0.0
        self.backup2LookedPowerB: float = 0.0
        self.backup2LookedPowerC: float = 0.0
        self.backup2TodayEnergy: float = 0.0
        self.backup2TodayEnergyStr: str = ''
        self.backup2MonthEnergy: float = 0.0
        self.backup2MonthEnergyStr: str = ''
        self.backup2YearEnergy: float = 0.0
        self.backup2YearEnergyStr: str = ''
        self.backup2TotalEnergy: float = 0.0
        self.backup2TotalEnergyStr: str = ''
        self.acCoupledTodayEnergy: float = 0.0
        self.acCoupledTodayEnergyStr: str = ''
        self.acCoupledMonthEnergy: float = 0.0
        self.acCoupledMonthEnergyStr: str = ''
        self.acCoupledYearEnergy: float = 0.0
        self.acCoupledYearEnergyStr: str = ''
        self.acCoupledTotalEnergy: float = 0.0
        self.acCoupledTotalEnergyStr: str = ''
        self.energyControl: str = ''
        self.energyControl00: int = 0
        self.energyControl01: int = 0
        self.pumpControl: str = ''
        self.pumpControl00: int = 0
        self.gridPortDeviceType: int = 0
        self.cpldVer: str = ''
        self.hmiVersionAll: str = ''
        self.dspmVersionAll: str = ''
        self.dspsVersionAll: str = ''
        self.hmilcdVersionAll: str = ''
        self.cpldVersionAll: str = ''
        self.sphVersionAll: str = ''
        self.afciVersionAll: str = ''
        self.bat1BmsVer: str = ''
        self.bat1DcdcVer: str = ''
        self.bat2BmsVer: str = ''
        self.bat2DcdcVer: str = ''
        self.showChipEvent: bool = False
        self.showDebugParam: bool = False
        self.dataTimestampStr: str = ''
        self.existEpm: bool = False
        self.model3P3W: int = 0
        self.isShowApparent: int = 0
        self.familyLoadPowerPec: str = ''
        self.psum: float = 0.0
        self.psumCal: float = 0.0
        self.bypassLoadPowerOriginal: float = 0.0
        self.reactivePowerStr: str = ''
        self.apparentPowerStr: str = ''
        self.backup2PowerOriginal: float = 0.0
        self.dcPacStr: str = ''
        self.psumCalStr: str = ''
        self.psumStr: str = ''

    def _from_json(self, json_data) -> SolisInverter:
        if json_data:
            for key, value in json_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        return self
    
    def get_charge_discharge_schedules(self) -> ChargeDischargeSchedule:
        if self.__parent__:
            self.charge_discharge_schedule = self.__parent__.get_charge_discharge_schedule(self.sn)
            return self.charge_discharge_schedule
    
    def set_charge_discharge_schedules(self, charge_discharge_schedule: ChargeDischargeSchedule) -> SolisSetResult:
        if self.__parent__:
            return self.__parent__.set_inverter_charge_discharge_schedule(self.id, self.sn, charge_discharge_schedule)
    
    def _to_json(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}


class ScheduleDateTime():
    def __init__(self):
        self.start: datetime
        self.end: datetime


class ScheduleDate():
    def __init__(self):
        self.start: date = date(1970, 1, 1)
        self.end: date = date(1970, 1, 1)


class ChargeData():
    def __init__(self):
        self.current: int = 0
        self.start: time = time(0, 0, 0, 0)
        self.end: time = time(0, 0, 0, 0)


class Schedule():
    def __init__(self):
        self.charge: ChargeData = ChargeData()
        self.discharge: ChargeData = ChargeData()


class ChargeDischargeSchedule():

    def __init__(self):
        self.one: Schedule = Schedule()
        self.two: Schedule = Schedule()
        self.three: Schedule = Schedule()
    
    def to_value(self) -> str:
        value = f"{self.one.charge.current},{self.one.discharge.current},{self.one.charge.start.strftime('%H:%M')},{self.one.charge.end.strftime('%H:%M')},{self.one.discharge.start.strftime('%H:%M')},{self.one.discharge.end.strftime('%H:%M')},{self.two.charge.current},{self.two.discharge.current},{self.two.charge.start.strftime('%H:%M')},{self.two.charge.end.strftime('%H:%M')},{self.two.discharge.start.strftime('%H:%M')},{self.two.discharge.end.strftime('%H:%M')},{self.three.charge.current},{self.three.discharge.current},{self.three.charge.start.strftime('%H:%M')},{self.three.charge.end.strftime('%H:%M')},{self.three.discharge.start.strftime('%H:%M')},{self.three.discharge.end.strftime('%H:%M')}"
        return value
    
    def _to_json(self) -> dict:
        json_obj = {}


class SolisSetResult():
    def __init__(self):
        self.success: bool = True
        self.error: str = ""
        self.message: str = ""


class SolisCloud():
    class RequestsSession(Session):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
        def request(self, method, url, **kwargs):
            response = super().request(method, url, **kwargs)
            
            if response.status_code == 429:
                print(f"Rate limit hit: {url} with status 429. Retrying...")
                raise RequestException("Rate limit exceeded")
            
            return response

        def get(self, url, **kwargs):
            return self.request('GET', url, **kwargs)

        def post(self, url, **kwargs):
            return self.request('POST', url, **kwargs)

        def put(self, url, **kwargs):
            return self.request('PUT', url, **kwargs)

        def delete(self, url, **kwargs):
            return self.request('DELETE', url, **kwargs)

    def __init__(self, key_id: str, key_secret: str, base_url: str = "https://www.soliscloud.com:13333"):
        """_summary_
        This class provides connectivity to the SolisCloud API.

        Args:
            base_url (str): The Base URL for SolisCloud API (typically https://www.soliscloud.com:13333)
            key_id (str): Your Key ID as provided in your SolicCloud account
            key_secret (str): Your Key Secret as provided in your SolicCloud account
        """
        self.key_id: str = key_id
        self.key_secret: str = key_secret
        self.base_url: str = base_url
        self.client = self.RequestsSession()
        self.headers = {}
    
    def __generate_authorization__(self, verb: str = "POST", body: str = "", content_type: str = "application/json", uri: str = "/"):
        now = datetime.now(pytz.UTC).strftime("%a, %d %b %Y %H:%M:%S GMT")
        content_md5 = b64encode(hashlib.md5(body.encode()).digest()).decode()
        message = ("\n".join([verb, content_md5, content_type, now, uri]))
        sign = b64encode(hmac.new(self.key_secret.encode(), msg=message.encode(), digestmod=hashlib.sha1).digest())
        self.headers = {
            "Authorization": f"API {self.key_id}:{sign.decode()}",
            "Content-Type": content_type,
            "Content-MD5": content_md5,
            "Date": now
        }
    
    def __expose_error__(self, res_json) -> str:
        error_message = ""
        data = res_json.get('data', {}) or {}
        for item in data:
            msg = item.get('msg', '') or ''
            if msg:
                error_message = f"{error_message}, {msg}"
        return error_message
    
    def __get_start_end_times__(self, data) -> Optional[tuple[time, time]]:
        ret_val = None
        try:
            data_split = data.split("-")
            start_time = data_split[0]
            end_time = data_split[1]
            ret_val = start_time, end_time
        except:
            ret_val = None
        return ret_val

    def list_stations(self, pageNo: int = 1, pageSize: int = 20, NmiCode: str = None, **kwargs) -> tuple[StatusVo, list[SolisStation]]:
        has_more = True
        stations: list[SolisStation] = []
        status_vo: StatusVo = StatusVo()
        while has_more:
            body = {
                "pageNo": pageNo, 
                "pageSize": pageSize
            }
            if NmiCode:
                body.update({
                    "NmiCode": NmiCode
                })
            for k, v in kwargs:
                body.update({
                    k: v
                })
            uri = "/v1/api/userStationList"
            url = f"{self.base_url}{uri}"
            self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
            res = self.client.post(url, json=body, headers=self.headers)
            if res.status_code == 200:
                res_json = res.json()
                data = res_json.get('data', {})
                station_status_vo = data.get('stationStatusVo', {})
                page = data.get('page', {})
                total_pages = page.get('pages', 1)
                if total_pages > pageNo:
                    has_more = True
                else:
                    has_more = False
                station_list = page.get('records')
                status_vo._from_json(station_status_vo)
                [stations.append(SolisStation(self)._from_json(x)) for x in station_list]
                if has_more:
                    pageNo += 1
            else:
                has_more = False
                raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")
        return status_vo, stations
    
    def get_station_detail(self, id: int, nmiCode: str = None, **kwargs) -> SolisStation:
        body = {
            "id": id
        }
        if nmiCode:
            body.update({
                "nmiCode": nmiCode
            })
        for k,v in kwargs:
            body.update({
                k: v
            })
        uri = "/v1/api/stationDetail"
        url = f"{self.base_url}{uri}"
        self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
        res = self.client.post(url, json=body, headers=self.headers)
        if res.status_code == 200:
            res_json = res.json()
            success = res_json.get('success', False)
            msg = res_json.get('msg', '')
            if not success:
                raise SolisConnectException(f"There was an error - {msg} - {res.status_code} - {res.reason}")
            data = res_json.get('data', {}) or {}
            station = SolisStation()._from_json(data)
            return station
            
        else:
            raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")

    def list_epms(self, pageNo: int = 1, pageSize: int = 20, stationId: str = "", NmiCode: str = None, **kwargs) -> tuple[StatusVo, list[SolisEPM]]:
        has_more = True
        epms: list[SolisEPM] = []
        status_vo: StatusVo = StatusVo()
        while has_more:
            body = {
                "pageNo": pageNo, 
                "pageSize": pageSize
            }
            if NmiCode:
                body.update({
                    "NmiCode": NmiCode
                })
            if stationId:
                body.update({
                    "stationId": stationId
                })
            for k, v in kwargs:
                body.update({
                    k: v
                })
            uri = "/v1/api/epmList"
            url = f"{self.base_url}{uri}"
            self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
            res = self.client.post(url, json=body, headers=self.headers)
            if res.status_code == 200:
                res_json = res.json()
                success = res_json.get('success', False)
                msg = res_json.get('msg', '')
                if not success:
                    raise SolisConnectException(f"There was an error - {msg} - {res.status_code} - {res.reason}")
                data = res_json.get('data', {})
                station_status_vo = data.get('epmStatusVo', {})
                page = data.get('page', {})
                total_pages = page.get('pages', 1)
                if total_pages > pageNo:
                    has_more = True
                else:
                    has_more = False
                epm_list = page.get('records')
                status_vo._from_json(station_status_vo)
                [epms.append(SolisEPM(self)._from_json(x)) for x in epm_list]
                if has_more:
                    pageNo += 1
            else:
                has_more = False
                raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")
        return status_vo, epms

    def get_epm_detail(self, sn: int, **kwargs) -> SolisEPM:
        body = {
            "sn": sn
        }
        for k,v in kwargs:
            body.update({
                k: v
            })
        uri = "/v1/api/epmDetail"
        url = f"{self.base_url}{uri}"
        self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
        res = self.client.post(url, json=body, headers=self.headers)
        if res.status_code == 200:
            res_json = res.json()
            success = res_json.get('success', False)
            msg = res_json.get('msg', '')
            if not success:
                raise SolisConnectException(f"There was an error - {msg} - {res.status_code} - {res.reason}")
            data = res_json.get('data', {}) or {}
            epm = SolisEPM(self)._from_json(data)
            return epm
            
        else:
            raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")

    def get_epm_data_for_day(self, sn: str, dt: date, timeZone: int, searchinfo: list[EPMFields] = [], **kwargs) -> EPMDayData:
        body = {
            "sn": sn,
            "time": dt.strftime("%Y-%m-%d"),
            "timeZone": timeZone
        }
        if searchinfo:
            body.update({
                "searchinfo": ",".join(searchinfo)
            })
        for k, v in kwargs.items():
            body.update({
                k: v
            })
        uri = "/v1/api/epm/day"
        url = f"{self.base_url}{uri}"
        self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
        res = self.client.post(url, json=body, headers=self.headers)
        if res.status_code == 200:
            res_json = res.json()
            success = res_json.get('success', False)
            msg = res_json.get('msg', '')
            if not success:
                raise SolisConnectException(f"There was an error - {msg} - {res.status_code} - {res.reason}")
            data = res_json.get('data', {}) or {}
            day_data = EPMDayData()._from_json_(data)
            return day_data
        else:
            raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")
    
    def get_epm_data_for_month(self, sn: str, dt: date, **kwargs) -> EPMMonthYearData:
        body = {
            "sn": sn,
            "month": dt.strftime("%Y-%m")
        }
        for k, v in kwargs.items():
            body.update({
                k: v
            })
        uri = "/v1/api/epm/month"
        url = f"{self.base_url}{uri}"
        self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
        res = self.client.post(url, json=body, headers=self.headers)
        if res.status_code == 200:
            res_json = res.json()
            success = res_json.get('success', False)
            msg = res_json.get('msg', '')
            if not success:
                raise SolisConnectException(f"There was an error - {msg} - {res.status_code} - {res.reason}")
            data = res_json.get('data', {}) or {}
            month_data = EPMMonthYearData()._from_json_(data)
            return month_data
        else:
            raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")
    
    def get_epm_data_for_year(self, sn: str, dt: date, **kwargs) -> EPMMonthYearData:
        body = {
            "sn": sn,
            "year": dt.strftime("%Y")
        }
        for k, v in kwargs.items():
            body.update({
                k: v
            })
        uri = "/v1/api/epm/year"
        url = f"{self.base_url}{uri}"
        self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
        res = self.client.post(url, json=body, headers=self.headers)
        if res.status_code == 200:
            res_json = res.json()
            success = res_json.get('success', False)
            msg = res_json.get('msg', '')
            if not success:
                raise SolisConnectException(f"There was an error - {msg} - {res.status_code} - {res.reason}")
            data = res_json.get('data', {}) or {}
            year_data = EPMMonthYearData()._from_json_(data)
            return year_data
        else:
            raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")

    def list_collectors(self, page_number: int = 1, page_size: int = 20, nmi_code: str = None, station_id: int = None):
        args = [{k: v} for k, v in locals().items() if k != "self"]
        body = {}
        [body.update(x) for x in args]
        return_value = {}
        uri = "/v1/api/collectorList"
        url = f"{self.base_url}{uri}"
        self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
        res = self.client.post(url, json=body, headers=self.headers)
        if res.status_code == 200:
            return_value = res.json()
        return return_value
    
    def list_inverters(self, pageNo: int = 1, pageSize: int = 100, stationId: str = None, nmiCode: str = None, **kwargs) -> tuple[StatusVo, list[SolisInverter]]:
        isvo: StatusVo = StatusVo()
        solis_inverters: list[SolisInverter] = []
        has_more = True
        while has_more:
            body = {
                "pageNo": pageNo,
                "pageSize": pageSize
            }
            if stationId:
                body.update({
                    "stationId": stationId
                })
            if nmiCode:
                body.update({
                    "nmiCode": nmiCode
                })
            for k, v in kwargs:
                body.update({
                    k: v
                })
            uri = "/v1/api/inverterList"
            url = f"{self.base_url}{uri}"
            self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
            
            res = self.client.post(url, json=body, headers=self.headers)
            if res.status_code == 200:
                res_json = res.json()
                success = res_json.get('success', False)
                msg = res_json.get('msg', '')
                if not success:
                    has_more = False
                    raise SolisConnectException(f"There was an error - {msg}")
                data = res_json.get('data', {}) or {}
                inverter_status_vo = data.get('inverterStatusVo', {}) or {}
                isvo: StatusVo = StatusVo()._from_json(inverter_status_vo)
                page = data.get('page', {})
                total_pages = page.get('pages', 1)
                if total_pages > pageNo:
                    has_more = True
                else:
                    has_more = False
                records = page.get('records', []) or []
                [solis_inverters.append(SolisInverter(self)._from_json(x)) for x in records]
                if has_more:
                    pageNo += 1
                    body.update({
                        "pageNo": pageNo
                    })
            else:
                has_more = False
                raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")
        return isvo, solis_inverters

    def get_inverter_details(self, id: str, sn: str, **kwargs) -> SolisInverter:
        body = {
            "id": id,
            "sn": sn
        }
        for k, v in kwargs:
            body.update({
                k: v
            })
        uri = "/v1/api/inverterDetail"
        url = f"{self.base_url}{uri}"
        self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
        res = self.client.post(url, json=body, headers=self.headers)
        if res.status_code == 200:
            res_json = res.json()
            success = res_json.get('success', False)
            msg = res_json.get('msg', '')
            if not success:
                raise SolisConnectException(f"There was an error - {msg} - {res.status_code} - {res.reason}")
            data = res_json.get('data', {})
            inverter = SolisInverter(self)._from_json(data)
            inverter.charge_discharge_schedule = inverter.get_charge_discharge_schedules()
            return inverter
        else:
            raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")

    def set_inverter_charge_discharge_schedule(self, id: str, sn: str, schedule: ChargeDischargeSchedule) -> SolisSetResult:
        value = schedule.to_value()
        body = {
            "inverterSn": sn,
            "inverterId": id,
            "cid": 103,
            "value": value
        }
        return_value = {}
        uri = "/v2/api/control"
        url = f"{self.base_url}{uri}"
        self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
        res = self.client.post(url, json=body, headers=self.headers)
        res_json = res.json()
        result = SolisSetResult()
        if res.status_code == 200:
            data = res_json.get('data', []) or []
            if data:
                result.message = data[0].get('msg', '') or ''
            result.success = True
            result.error = ""
        else:
            error = self.__expose_error__(res_json)
            result.error = error
            result.success = False
        return result
    
    def get_charge_discharge_schedule(self, sn: str) -> ChargeDischargeSchedule:
        body = {
            "inverterSn": sn,
            "cid": 103,
        }
        uri = "/v2/api/atRead"
        url = f"{self.base_url}{uri}"
        self.__generate_authorization__("POST", json.dumps(body, separators=(',',':')), "application/json", uri)
        res = self.client.post(url, json=body, headers=self.headers)
        if res.status_code == 200:
            res_json = res.json()
            data = res_json.get('data', {}) or {}
            msg = data.get('msg', "") or ""
            if msg:
                msg_split: list = msg.split(",")
                s = ChargeDischargeSchedule()
                
                s.one.charge.current = msg_split.pop(0)
                s.one.discharge.current = msg_split.pop(0)
                s.one.charge.start, s.one.charge.end = self.__get_start_end_times__(msg_split.pop(0))
                s.one.discharge.start, s.one.discharge.end = self.__get_start_end_times__(msg_split.pop(0))
                
                s.two.charge.current = msg_split.pop(0)
                s.two.discharge.current = msg_split.pop(0)
                s.two.charge.start, s.two.charge.end = self.__get_start_end_times__(msg_split.pop(0))
                s.two.discharge.start, s.two.discharge.end = self.__get_start_end_times__(msg_split.pop(0))
                
                s.three.charge.current = msg_split.pop(0)
                s.three.discharge.current = msg_split.pop(0)
                s.three.charge.start, s.three.charge.end = self.__get_start_end_times__(msg_split.pop(0))
                s.three.discharge.start, s.three.discharge.end = self.__get_start_end_times__(msg_split.pop(0))
                return s
        else:
            raise SolisConnectException(f"There was an error - {res.status_code} - {res.reason}")
