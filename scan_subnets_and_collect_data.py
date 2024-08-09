import time
import os

from typing import Final, List, Tuple

from modules.NetworkScanner import NetworkScanner
from modules.WhatsminerCheck import WhatsminerCheck


# **


SUBNETS: Final[List] = [
    "192.168.0",
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

# Оптимально для 8 core && 16GB RAM
THREADS: Final[int] = 50

ASICS_IP_FOUND_IN_SUBNETS: [List[Tuple[str, str]]] = []
ASICS_DATA_FROM_FILE: [List[Tuple[str, str]]] = []

CURRENT_DIRECTORY: str = os.path.join(os.path.dirname(__file__))
FILE_NAME: str = "asics_data.txt"


# **


def write_to_file(filename: str, data: List[Tuple[str, str]]):
    with open(f"{CURRENT_DIRECTORY}\{filename}", 'w') as file:
        for ip, password in data:
            file.write(f"{ip}, {password}\n")


# **


if __name__ == "__main__":
    print(f"Задано потоков: {THREADS}")

    # **

    start_time = time.time()

    scan_subnets = NetworkScanner(SUBNETS, THREADS, WhatsminerCheck)
    scan_subnets.async_scan_subnets_and_collect_asics_ip()
    ASICS_IP_FOUND_IN_SUBNETS = scan_subnets.get_asics_ip_found()

    end_time = time.time()
    print('time: ', end_time - start_time)

    # **

    write_to_file(FILE_NAME, ASICS_IP_FOUND_IN_SUBNETS)

    print(f"Сбор данных об имеющихся Whats's в подсетях завершен. "
          f"Cм файл: {CURRENT_DIRECTORY}\\{FILE_NAME}")
