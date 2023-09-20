import http
import subprocess
import concurrent.futures
import threading

SUBNETS = [
    "192.168.0",
    # "192.168.1",
    # "192.168.2",
    # "192.168.3",
    # "192.168.4",
    # "192.168.5",
    # "192.168.6",
    # "192.168.7",
    # "192.168.8",
    # "192.168.9"
]

END_IP_ADDRESS_FOR_NETWORK = 254
THREADS_NUMBER = 150

# Мьютекс для синхронизации вывода
lock = threading.Lock()


# -----------------------------------------------------------------------------


# Функция для выполнения ping-запроса на указанный IP-адрес
def ping_all_devices_in_network(ip):
    # Для Windows используется -n, для Linux используется -c
    command = f"ping -c 1 {ip}"

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        return True
    else:
        return False


def check_whatsminer(ip):
    try:
        # response, content = http.request(f"http://{ip}", "GET")
        # if response.status == 200 and "whatsminer" in content.decode():
        response, content = http.client.HTTPConnection(ip, timeout=1).request("GET", "/")
        if response.status == 200 and "whatsminer" in content.decode():
            return True
    except:
        pass
    return False


# Функция для сканирования диапазона адресов в подсети
def scan_network_range(start, end, subnet):
    for i in range(start, end + 1):
        ip = f"{subnet}.{i}"

        if ping_all_devices_in_network(ip):
            with lock:
                print(f"Device found: {ip}")
                # print(f"Whatsminer found: {ip}")


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


#
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Задано потоков: {THREADS_NUMBER}")

    async_scan_subnets()

    input("Press Enter to exit...")
