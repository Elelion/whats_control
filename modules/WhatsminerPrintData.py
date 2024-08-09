class WhatsminerPrintData:
    def __init__(self, asics_detail):
        self.asics_detail = asics_detail

    def print_data(self):
        for key, data_list in self.asics_detail.items():
            if len(data_list[0]["errors"]) > 0:
                print("[", key, "]")

                print("Temp:", data_list[0]["temperature"])
                print("MHS av:", data_list[0]["mhs_av"])
                print("MHS 1m:", data_list[0]["mhs_1m"])
                print("MHS 15m:", data_list[0]["mhs_15m"])

                print("Env Temp:", data_list[0]["env_temp"])
                print("Fan Speed In", data_list[0]["fan_speed_in"])
                print("Fan Speed Out:", data_list[0]["fan_speed_out"])

                print("Power:", data_list[0]["power"])

                if len(data_list[0]["errors"]) > 0:
                    print("Errors!:")
                    print(data_list[0]["errors"])

                print("\n---\n")
