import time
import os

from typing import Final, List, Tuple

from modules.WhatsminerCollectData import WhatsminerCollectData
from modules.WhatsminerControl import WhatsminerControl
from modules.WhatsminerPrintData import WhatsminerPrintData
from whatsminer import WhatsminerAccessToken, WhatsminerAPI


# **


# Оптимально для 8 core && 16GB RAM
THREADS: Final[int] = 50

ASICS_DATA_FROM_FILE: [List[Tuple[str, str]]] = []

CURRENT_DIRECTORY: str = os.path.join(os.path.dirname(__file__))
FILE_NAME: str = "asics_data.txt"


# **


def load_data_from_file(filename: str):
    with open(f"{CURRENT_DIRECTORY}\{filename}", 'r') as file:
        for line in file:
            ip, password = line.strip().split(', ')
            ASICS_DATA_FROM_FILE.append((ip, password))


# **


if __name__ == "__main__":
    start_time = time.time()

    # TODO: в файле не обходимо внести пароли для найденных устр-в в ручную !!!

    load_data_from_file(FILE_NAME)
    print("Load from file - successfully \n\n")

    # **

    # Собираем все данные в ASICS_DATA
    whatsData = WhatsminerCollectData(ASICS_DATA_FROM_FILE)
    whatsData.collect_data()
    ASICS_DATA = whatsData.get_data()
    print("Collect data - successfully \n\n")

    # **

    # Просмотр What's у которых имеются ошибки
    # print_data = WhatsminerPrintData(ASICS_DATA)
    # print_data.print_data()
    # print("Print data - successfully \n\n")

    # **

    # Мониторинг What's
    control = WhatsminerControl(ASICS_DATA)
    control.control()
    control.send_data_for_site()

    # **

    end_time = time.time()
    print('time: ', end_time - start_time)


    # input("Press Enter to exit...")
