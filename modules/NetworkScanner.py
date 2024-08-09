import subprocess
import concurrent.futures
import threading
from typing import List, Type

from modules import AsicStatusInterface

# Мьютекс для синхронизации вывода
lock = threading.Lock()


# **


class NetworkScanner():
    def __init__(
            self,
            subnets,
            threads_number,
            get_asic_status: Type[AsicStatusInterface]
    ):
        self.subnets = subnets
        self.threads_number = threads_number
        self.whatsminer_check = get_asic_status

        self.end_ip_address_for_network: [int] = 254
        self.lock = threading.Lock()
        self.asics_ip_found: [List] = []

    def _ping_device(self, ip):
        timeout_ms = 100

        # Для Windows используется -n, для Linux используется -c
        command = f"ping -n 1 -w {timeout_ms} {ip}"

        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)

        if "TTL" in result.stdout:
            # Аналогично: if WhatsminerCheck.get_asic_status(ip):
            if self.whatsminer_check.get_asic_status(ip):
                return True
        return False

    def _scan_network_range(self, start, end, subnet):
        for i in range(start, end + 1):
            ip = f"{subnet}.{i}"
            if self._ping_device(ip):
                with self.lock:
                    self.asics_ip_found.append((ip, 'admin'))

    def _async_scan_network(self, subnet):
        futures = []
        addresses_per_thread = \
            self.end_ip_address_for_network // self.threads_number

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads_number) as executor:
            for i in range(self.threads_number):
                start = 1 + i * addresses_per_thread

                end = start + addresses_per_thread - 1 \
                    if i != self.threads_number - 1 \
                    else self.end_ip_address_for_network

                futures.append(executor.submit(
                    self._scan_network_range,
                    start,
                    end,
                    subnet))

        for future in concurrent.futures.as_completed(futures):
            future.result()

    def async_scan_subnets_and_collect_asics_ip(self):
        for subnet in self.subnets:
            print(f"Scanning subnet: {subnet}.1 - "
                  f"{subnet}.{self.end_ip_address_for_network}")
            self._async_scan_network(subnet)

    def get_asics_ip_found(self):
        return self.asics_ip_found
