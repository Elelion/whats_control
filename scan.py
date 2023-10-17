import http
import subprocess
import concurrent.futures
import threading
import asyncio
import aiohttp
import time

from typing import Final
from whatsminer import WhatsminerAccessToken, WhatsminerAPI


# **


SUBNETS = [
    # "192.168.0",
    "192.168.1",
    "192.168.2",
    "192.168.3",
    "192.168.4",
    "192.168.5",
    "192.168.6",
    "192.168.7",
    "192.168.8",
    "192.168.9"
]


END_IP_ADDRESS_FOR_NETWORK: Final = 254

# Оптимально для 8 core && 16GB RAM
THREADS_NUMBER: Final = 50

# Мьютекс для синхронизации вывода
lock = threading.Lock()


# -----------------------------------------------------------------------------


class WhatsminerDetect:
    def __init__(self, asic_ip):
        self.asic_ip = asic_ip

    @staticmethod
    def __check_is_asic(token, json_summary):
        ip = token.ip_address
        elapsed = json_summary['SUMMARY'][0]['Elapsed']
        uptime = json_summary['SUMMARY'][0]['Uptime']

        # если данные получены с асика, то True, если нет то False
        if ip != "" and elapsed != "" and uptime != "":
            return True
        else:
            return False

    @staticmethod
    def get_asic_status(ip_address):
        try:
            token = WhatsminerAccessToken(
                ip_address=ip_address,
                admin_password='admin')

            json_summary = WhatsminerAPI.get_read_only_info(
                access_token=token,
                cmd='summary'
            )

            return WhatsminerDetect.__check_is_asic(token, json_summary)
        except Exception as e:
            return False


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


# Функция для выполнения ping-запроса на указанный IP-адрес
def ping_all_devices_in_network(ip):
    timeout_ms = 100

    # Для Windows используется -n, для Linux используется -c
    command = f"ping -n 1 -w {timeout_ms} {ip}"

    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)

    # Если результат команды ping содержит "TTL", это успешный пинг
    if "TTL" in result.stdout:
        if WhatsminerDetect.get_asic_status(ip):
            return True
    else:
        return False


# Функция для сканирования диапазона адресов в подсети
def scan_network_range(start, end, subnet):
    for i in range(start, end + 1):
        ip = f"{subnet}.{i}"

        if ping_all_devices_in_network(ip):
            with lock:
                print(f"Whatsminer found: {ip}")


# Функция для асинхронного сканирования подсети
def async_scan_network(subnet):
    futures = []  # Список для хранения будущих результатов асинхронных задач
    num_threads = THREADS_NUMBER  # Количество потоков для асинхронного сканирования
    addresses_per_thread = END_IP_ADDRESS_FOR_NETWORK // num_threads  # Количество адресов на один поток

    # Создаем пул потоков с максимальным числом потоков равным num_threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(num_threads):
            start = 1 + i * addresses_per_thread  # Начальный адрес для данного потока
            end = start + addresses_per_thread - 1 if i != num_threads - 1 else END_IP_ADDRESS_FOR_NETWORK

            # Запускаем задачу асинхронного сканирования для заданного диапазона адресов в подсети
            futures.append(executor.submit(scan_network_range, start, end, subnet))

    # Дожидаемся завершения всех асинхронных задач
    for future in concurrent.futures.as_completed(futures):
        future.result()


def async_scan_subnets():
    for subnet in SUBNETS:
        print(f"Scanning subnet: {subnet}.1 - {subnet}.{END_IP_ADDRESS_FOR_NETWORK}")
        async_scan_network(subnet)


# -----------------------------------------------------------------------------


if __name__ == "__main__":
    print(f"Задано потоков: {THREADS_NUMBER}")

    # begin scan
    start_time = time.time()
    async_scan_subnets()
    end_time = time.time()
    print('time: ', end_time - start_time)

    # input("Press Enter to exit...")
