import re
import requests

from typing import Final
from modules.MailSend import MailSend
from modules.WhatsminerPrintData import WhatsminerPrintData
from whatsminer import WhatsminerAccessToken, WhatsminerAPI


class WhatsminerControl:
    def __init__(self, asics_detail):
        # temperatures
        self.TEMP_PLATE: Final = 84.0
        self.TEMP_ENV_MAX: Final = 45.0
        self.TEMP_ENV_MIN: Final = -1.0
        self.HASHRATE_DIFFERENCE: Final = 5

        # hashrates
        self.MHS_AV = 0
        self.MHS_1M = 0
        self.MHS_15M = 0

        # fans
        self.FAN_SPEED_IN_MAX = 7500
        self.FAN_SPEED_OUT_MAX = 7500
        self.FAN_SPEED_IN_MIN = 1000
        self.FAN_SPEED_OUT_MIN = 1000

        # power
        self.POWER_MAX = 3800
        self.POWER_MIN = 2900

        # uptime
        self.UPTIME_MINUTES = 40

        # message for email
        self.message_data = {}
        self.message_status = False

        # **

        self.asics_detail = asics_detail
        self.asics_data_for_site = {}

    def control(self):
        for ip, data_list in self.asics_detail.items():
            for data in data_list:
                token = data['token']
                asic_name = data['pools_worker_name']

                # prepare data for: __control_hashrate()
                extract_hashrate_fom_worker_name = \
                    self.__extract_nominal_hashrate_from_worker(asic_name)

                hashrate_data = {
                    'extract_hashrate_fom_worker_name': extract_hashrate_fom_worker_name,
                    # 'factory_ths': self.__convert_ghs_to_ths(data['factory_ghs']),
                    'mhs_av': data['mhs_av'],
                    'mhs_1m': data['mhs_1m'],
                    'mhs_15m': data['mhs_15m']
                }

                # prepare full data for: email send
                asic_data = {
                    'temperature': data['temperature'],
                    'env_temp': data['env_temp'],
                    'fan_speed_in': data['fan_speed_in'],
                    'fan_speed_out': data['fan_speed_out'],
                    'power': data['power'],

                    'pools_worker_name': data['pools_worker_name'],
                }

                uptime_minutes = data['uptime'] / 60
                errors = data['errors']

                # log
                print('\n\n=> [{} - {}] \n factory_ghs: {} \n extract: {} \n uptime (min): {} \n errors: {}'.format(
                    ip,
                    asic_name,
                    self.__convert_ghs_to_ths(data['factory_ghs']),
                    extract_hashrate_fom_worker_name,
                    uptime_minutes,
                    errors))

                # **

                # self.__control_errors(token, ip, hashrate_data, asic_data, errors)
                self.__control_env_temp(token, ip, data['temperature'], data['env_temp'])
                # self.__control_fans(token, ip, data['fan_speed_in'], data['fan_speed_out'])
                self.__control_hashrate(token, ip, hashrate_data, uptime_minutes)
                self.__control_power(token, ip, data['power'])

                self.__message_alert(asic_name)

                # собираем данные для отправки на сайт
                self.__update_asics_data_for_site(asic_name, data['env_temp'])

    # **

    def __control_errors(self, token, ip, hashrate_data, asic_data, errors):
        if errors:
            print(f'WhatsminerControl - Обнаружены ошибки в: {ip}')
            print(f'Errors: {errors}')

            # Вариант записи в строку №1
            hashrate_data_str = ''
            for key, val in hashrate_data.items():
                hashrate_data_str += f'{key}: {val}\n'

            # Вариант записи в строку №2
            asic_data_str = '\n'.join([f'{key}: {val}' for key, val in asic_data.items()])

            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot", additional_params={"respbefore": "true"})
            # print(f'WhatsminerControl - {ip} успешно перезагружен...')

            # Отправляем на почту
            title = f'{ip} - is Errors!!!'
            msg = '{} \n {} \n\n errors: {}'.format(
                hashrate_data_str,
                asic_data_str,
                errors
            )

            # self.__send_mail(title, msg, True)

    def __control_env_temp(self, token, ip, temperature, env_temp):
        title = ''
        msg = f'Current env_temp: {env_temp} \n temperature: {temperature}\n\n'

        # for hot
        if temperature >= self.TEMP_PLATE or env_temp >= self.TEMP_ENV_MAX:
            print(f'WhatsminerControl - повышенная температура: {ip}')
            print('temperature: {} \n env_temp: {}'.format(temperature, env_temp))

            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")
            # print(f'WhatsminerControl - {ip} успешно перезагружен...')

            title = f'{ip} - is Hot!!! \n\n'
            # self.__send_mail(title, msg, True)

        # for cold
        if env_temp <= self.TEMP_ENV_MIN:
            print(f'WhatsminerControl - пониженная температура: {ip}')
            print('env_temp', env_temp)

            title = f'{ip} - is Cold!!! \n\n'
            # self.__send_mail(title, msg, False)

        # for hot or cold
        if (temperature >= self.TEMP_PLATE or env_temp >= self.TEMP_ENV_MAX
                or env_temp <= self.TEMP_ENV_MIN):
            env_temp_data = {
                'title': title,
                'message': msg,
            }

            self.message_data['env_temp'] = env_temp_data
            self.message_status = True

    def __control_fans(self, token, ip, fan_speed_in, fan_speed_out):
        title = ''
        msg = f'Current speed: in: {fan_speed_in} and out: {fan_speed_out}'
        print('fans: ', msg)

        if fan_speed_in > self.FAN_SPEED_IN_MAX or (fan_speed_out < self.FAN_SPEED_IN_MAX and fan_speed_out > 1000):
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")
            # print(f'WhatsminerControl - {ip} успешно перезагружен...')

            title = f"{ip} - high fan speed!!!"
            self.message_status = True

            # self.__send_mail(title, msg, True)

        if fan_speed_in <= self.FAN_SPEED_IN_MIN or fan_speed_out <= self.FAN_SPEED_IN_MIN:
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")
            # print(f'WhatsminerControl - {ip} успешно перезагружен...')

            title = f'{ip} - low fan speed!!!'

            # self.__send_mail(title, msg, True)

        if (fan_speed_in > self.FAN_SPEED_IN_MAX or fan_speed_out > self.FAN_SPEED_IN_MAX or
                fan_speed_in <= self.FAN_SPEED_IN_MIN or fan_speed_out <= self.FAN_SPEED_IN_MIN):

            fans_data = {
                'title': title,
                'message': msg,
            }

            self.message_data['fans'] = fans_data
            self.message_status = True

    def __control_hashrate(self, token, ip, hashrate_data, uptime_minutes):
        average_hashrate = 0.0
        extract_hashrate_fom_worker_name = ''
        title = ''
        msg = ''

        for key, val in hashrate_data.items():
            # for debug
            # print(key,val)
            if key == 'extract_hashrate_fom_worker_name':
                extract_hashrate_fom_worker_name = val

            if key != 'extract_hashrate_fom_worker_name' and (type(val) == str or type(val) == int):
                average_hashrate += float(val)

                # for debug
                # print("->", val)

        # average_hashrate / 3
        average_val_all_hashrate = len(hashrate_data) - 1
        round_average_hashrate = round(average_hashrate / average_val_all_hashrate, 2)
        print('round_average_hashrate: ', round_average_hashrate, ' th')

        # for debug
        # print(f"round_average_hashrate: {round_average_hashrate} / {ip} : {average_val_all_hashrate}")

        nominal_hashrate = int(extract_hashrate_fom_worker_name) - self.HASHRATE_DIFFERENCE
        if uptime_minutes > self.UPTIME_MINUTES and int(round_average_hashrate) < (int(nominal_hashrate)) and round_average_hashrate > 0:
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")
            # print(f"WhatsminerControl - {ip} успешно перезагружен...")

            title = f'{ip} - low hashrate!!!'
            msg = 'Current round_average_hashrate: {} extract_hashrate_fom_worker_name: {}'.format(
                round_average_hashrate,
                extract_hashrate_fom_worker_name)

            hashrate_data = {
                'title': title,
                'message': msg,
            }

            self.message_data['hashrate'] = hashrate_data
            self.message_status = True

            # self.__send_mail(title, msg, True)

    def __control_power(self, token, ip, power):
        if (power > self.POWER_MAX and power > 100) or (power < self.POWER_MIN and power > 100):
            # WhatsminerAPI.exec_command(access_token=token, cmd="reboot")
            # print('WhatsminerControl - {ip}:')

            title = f'{ip} - problem with power!!!'
            msg = f'Current power: {power}'

            power_data = {
                'title': title,
                'message': msg,
            }

            self.message_data['power'] = power_data
            self.message_status = True

            # self.__send_mail(title, msg, True)

    def __message_alert(self, asic_name):
        if self.message_status:
            result_string = ""

            for key, value in self.message_data.items():
                result_string += f"{key}: {value}\n"

            print(result_string)
            self.message_status = False

            self.__send_mail(result_string, True)

            # env_temp_message = self.message_data['env_temp']['title']

            # self.message_data['env_temp'] = env_temp_data

    # **

    def __update_asics_data_for_site(self, asic_name, env_temp):
        # Обновляем словарь asics_data
        self.asics_data_for_site[asic_name] = {
            'env_temp': env_temp
        }

    def send_data_for_site(self):
        site_controller_url = 'http://aititaim.proff-l.ru/monitoring/receive_data/'

        try:
            # Отправляем POST-запрос с данными
            response = requests.post(site_controller_url, json=self.asics_data_for_site)

            # Проверяем статус ответа
            if response.status_code == 200:
                print(f"Данные успешно отправлены")
            else:
                print(f"Ошибка при отправке данных: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка соединения: {e}")

    # **

    # ищем в имени типа MSKxM30x108x1004097 или 6-3-2_65_M20S
    # номинальный хешрейт, который мы берем из имени воркера
    # в виде 108 или 65 - получаем эти значения через регулярные выр-ия
    @classmethod
    def __extract_nominal_hashrate_from_worker(cls, worker):
        pattern1 = r'\d+_(\d+)_'
        match1 = re.search(pattern1, worker)

        if match1:
            result_match = match1.group(1)
            return result_match

        parts = worker.split('x')

        if len(parts) > 3:
            hashrate = parts[3]
            return hashrate

        return None

    @classmethod
    def __convert_ghs_to_ths(cls, ghs):
        hashrate_th = ghs / 1000
        return f"{hashrate_th:.2f}"

    @classmethod
    def __send_mail(cls, msg, status_asic):
        operation = 'Check is this asic...' if status_asic == True else ''
        MailSend(operation + '\n\n' + msg)
