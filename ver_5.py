import re

from typing import Final
from whatsminer import WhatsminerAccessToken, WhatsminerAPI
from MailSend import MailSend

ASICS_DETAIL: Final = {}


# -----------------------------------------------------------------------------


# it's ok !!!
# MailSend('проверка')
# MailSend('проверка - 2')


# -----------------------------------------------------------------------------


# it's ok !!!
class WhatsminerMonitorCollectData:
    def __init__(self, asics):
        self.asics = asics
        self.tokens = []
        self.asics_detail = {}

    @classmethod
    def __convert_mhs_to_th_str(cls, mhs):
        hashrate_th = mhs / 1e6
        return f"{hashrate_th:.2f}"

    def __write_asic_data(self, token, json_summary, json_pool, error_msg):
        ip = token.ip_address
        temperature = json_summary['SUMMARY'][0]['Temperature']

        mhs_av = self.__convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS av'])
        mhs_1m = self.__convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS 1m'])
        mhs_15m = self.__convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS 15m'])
        rejected = json_summary['SUMMARY'][0]['Rejected']

        env_temp = json_summary['SUMMARY'][0]['Env Temp']
        fan_speed_in = json_summary['SUMMARY'][0]['Fan Speed In']
        fan_speed_out = json_summary['SUMMARY'][0]['Fan Speed Out']

        pools_worker_name = json_pool['POOLS'][0]['User']

        factory_ghs = json_summary['SUMMARY'][0]['Factory GHS']
        power = json_summary['SUMMARY'][0]['Power']

        # **

        asic_data = {
            "token": token,
            "temperature": temperature,
            "mhs_av": mhs_av,
            "mhs_1m": mhs_1m,
            "mhs_15m": mhs_15m,
            "rejected": rejected,
            "env_temp": env_temp,
            "fan_speed_in": fan_speed_in,
            "fan_speed_out": fan_speed_out,
            "factory_ghs": factory_ghs,
            "power": power,

            "pools_worker_name": pools_worker_name,

            "errors": []
        }

        # **

        if ip not in self.asics_detail:
            self.asics_detail[ip] = []

        self.asics_detail[ip].append(asic_data)
        self.__write_asic_errors(error_msg, ip)

    def __write_asic_errors(self, error_msg, ip):
        if type(error_msg) == str:
            if "error_code" in error_msg:
                error_info = error_msg["error_code"]

                for code in error_info:
                    self.asics_detail[ip][-1]["errors"].append(code)

        elif type(error_msg) == dict:
            error_info = error_msg.get("error_code", [])

            if error_info:
                for code_info in error_info:
                    for code in code_info:
                        self.asics_detail[ip][-1]["errors"].append(code)

    def monitor(self):
        for asic_info in self.asics:
            self.tokens.append(WhatsminerAccessToken(
                ip_address=asic_info[0],
                admin_password=asic_info[1]))

        for token in self.tokens:
            json_summary = WhatsminerAPI.get_read_only_info(
                access_token=token,
                cmd="summary")

            json_pool = WhatsminerAPI.get_read_only_info(
                access_token=token,
                cmd="pools")

            try:
                error_code_json = WhatsminerAPI.get_read_only_info(
                    access_token=token,
                    cmd="get_error_code")

                error_msg = error_code_json.get("Msg")
            except Exception as e:
                # если skip_err, то уведомляем !!!
                error_msg = ['skip_err']

            self.__write_asic_data(token, json_summary, json_pool, error_msg)

    def get_asics_detail(self):
        return self.asics_detail


# -----------------------------------------------------------------------------


# it's ok !!!
# todo: доработать что бы данный класс выводил инфо при
#  нахождении ошибки в WhatsminerMonitorControl
class WhatsminerMonitorPrintData:
    def __init__(self, asics_detail):
        self.asics_detail = asics_detail

    def print_detail(self):
        for key, val in self.asics_detail.items():
            print("[", key, "]")

            print("Temp:", val[0]["temperature"])
            print("MHS av:", val[0]["mhs_av"])
            print("MHS 1m:", val[0]["mhs_1m"])
            print("MHS 15m:", val[0]["mhs_15m"])
            print("Rejected:", val[0]["rejected"])

            print("Env Temp:", val[0]["env_temp"])
            print("Fan Speed In", val[0]["fan_speed_in"])
            print("Fan Speed Out:", val[0]["fan_speed_out"])

            print("Power:", val[0]["power"])

            if len(val[0]["errors"]) > 0:
                print("Errors!:")
                print(val[0]["errors"])

            print("\n---\n")


# -----------------------------------------------------------------------------


class WhatsminerMonitorControl:
    def __init__(self, asics_detail):
        # temperatures
        self.TEMP_PLATE: Final = 79.0
        self.TEMP_ENV_MAX: Final = 39.0
        self.TEMP_ENV_MIN: Final = 3.0
        self.HASHRATE_DIFFERENCE:Final = 3

        # hashrates
        self.MHS_AV = 0
        self.MHS_1M = 0
        self.MHS_15M = 0
        self.REJECTED = 100

        # fans
        self.FAN_SPEED_IN_MAX = 7500
        self.FAN_SPEED_OUT_MAX = 7500
        self.FAN_SPEED_IN_MIN = 1500
        self.FAN_SPEED_OUT_MIN = 1500

        # power
        self.POWER_MAX = 3700
        self.POWER_MIN = 2900

        # **

        self.asics_detail = asics_detail

    def control(self):
        for ip, data_list in self.asics_detail.items():
            for data in data_list:
                token = data["token"]

                # prepare data for: __control_hashrate()
                factory_ths = self.__convert_ghs_to_ths(data["factory_ghs"])
                extract_hashrate_fom_worker_name = \
                    self.__extract_nominal_hashrate_from_worker(data["pools_worker_name"])

                hashrate_list = {
                    "extract_hashrate_fom_worker_name": extract_hashrate_fom_worker_name,
                    "factory_ths": factory_ths,
                    "mhs_av": data["mhs_av"],
                    "mhs_1m": data["mhs_1m"],
                    "mhs_15m": data["mhs_15m"]
                }

                # **

                self.__control_temperature(token, ip, data["temperature"], data["env_temp"])
                self.__control_fans(token, ip, data["fan_speed_in"], data["fan_speed_out"])
                self.__control_hashrate(token, ip, hashrate_list)
                self.__control_power(token, ip, data["power"])
                self.__control_rejected(token, ip, data["rejected"])

    # **

    def __control_temperature(self, token, ip, temperature, env_temp):
        # for hot
        if temperature >= self.TEMP_PLATE or env_temp >= self.TEMP_ENV_MAX:
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")

            title = f"{ip} - is Hot!!! \n\n"
            msg = f"Current temperature: {temperature}, env_temp: {env_temp}\n"
            self.__send_mail(title, msg, True)

        # for cold
        if env_temp <= self.TEMP_ENV_MIN:
            title = f"{ip} - is Cold!!! \n\n"
            msg = f"Current env_temp: {env_temp}"
            self.__send_mail(title, msg, False)

    def __control_fans(self, token, ip, fan_speed_in, fan_speed_out):
        msg = f"Current speed: in: {fan_speed_in} and out: {fan_speed_out}\n"

        if fan_speed_in > self.FAN_SPEED_IN_MAX or fan_speed_out > self.FAN_SPEED_IN_MAX:
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")

            title = f"{ip} - high fan speed!!! \n\n"
            self.__send_mail(title, msg, True)

        if fan_speed_in <= self.FAN_SPEED_IN_MIN or fan_speed_out <= self.FAN_SPEED_IN_MIN:
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")

            title = f"{ip} - low fan speed!!! \n\n"
            self.__send_mail(title, msg, True)

    def __control_hashrate(self, token, ip, hashrate_list):
        average_hashrate = 0.0
        extract_hashrate_fom_worker_name = ""

        for key, val in hashrate_list.items():
            if key == "extract_hashrate_fom_worker_name":
                extract_hashrate_fom_worker_name = val

            average_hashrate += float(val)

        # average_hashrate / 4
        average_val_all_hashrate = len(hashrate_list) - 1
        round_average_hashrate = round(average_hashrate / average_val_all_hashrate, 2)

        if round_average_hashrate < (extract_hashrate_fom_worker_name - self.HASHRATE_DIFFERENCE):
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")

            title = f"{ip} - low hashrate!!! \n\n"
            msg = f"Current round_average_hashrate: {round_average_hashrate}\n"
            self.__send_mail(title, msg, True)

    def __control_power(self, token, ip, power):
        if power > self.POWER_MAX or power < self.POWER_MIN:
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")

            title = f"{ip} - problem with power!!! \n\n"
            msg = f"Current power: {power}\n"
            self.__send_mail(title, msg, True)

    def __control_rejected(self, token, ip, rejected):
        if rejected > self.REJECTED:
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")

            title = f"{ip} - too much rejected!!! \n\n"
            msg = f"Current rejected: {rejected}\n"
            self.__send_mail(title, msg, True)

    # **

    # ищем в имени типа MSKxM30x108x1004097 или 6-3-2_65_M20S
    # номинальный хешрейт, который мы берем из имени воркера
    # в виде 108 или 65 - получаем эти значения через регулярные выр-ия
    @classmethod
    def __extract_nominal_hashrate_from_worker(cls, worker):
        match = re.search(r'\d+_(\d+)_', worker)
        if match:
            return int(match.group(1))
        return None

        pattern1 = r'\d+_(\d+)_'
        pattern2 = r'(?<=\D)\d+(?=\D*\d*$)'

        match1 = re.search(pattern1, worker)
        match2 = re.search(pattern2, worker)

        if match1:
            result_match = match1.group(1)
            return result_match

        elif match2:
            result_match = match2.group()
            return result_match

        else:
            return ''

    @classmethod
    def __convert_ghs_to_ths(cls, ghs):
        hashrate_th = ghs / 1000
        return f"{hashrate_th:.2f}"

    @classmethod
    def __send_mail(cls, title, msg, status_asic):
        operation = "asic has been rebooted..." if status_asic == True else ""
        MailSend(title + msg + operation)


# -----------------------------------------------------------------------------


asics_list = [
    # ('192.168.2.28', 'admin'),
    # ('192.168.2.29', 'admin'),
    # ('192.168.5.71', 'admin'),
    # ('192.168.2.30', 'admin'),
    ('192.168.6.39', 'admin'),
    ('192.168.6.19', 'admin'),
    # ('192.168.9.73', 'admin'),
    # ('192.168.1.37', 'admin'),
]


# **


print("ver_5")
# monitor = WhatsminerMonitorTest(asics_list)
# monitor.monitor()

monitor = WhatsminerMonitorCollectData(asics_list)
monitor.monitor()
ASICS_DETAIL = monitor.get_asics_detail()

print_asisc_detail = WhatsminerMonitorPrintData(ASICS_DETAIL)
print_asisc_detail.print_detail()

# control = WhatsminerMonitorControl(ASICS_DETAIL)
# control.control()
