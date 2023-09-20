from whatsminer import WhatsminerAccessToken, WhatsminerAPI

class WhatsminerMonitor:
    def __init__(self, asics):
        self.asics = asics
        self.tokens = []

        self.ip = 0
        self.temperature = 0

        self.mhs_av = 0
        self.mhs_1m = 0
        self.mhs_15m = 0
        self.rejected = 0

        self.ent_temp = 0
        self.chip_temp_avg = 0
        self.fan_speed_in = 0
        self.fan_speed_out = 0

        self.power = 0

        self.errors = []

    @classmethod
    def __convert_mhs_to_th_str(cls, mhs):
        hashrate_th = mhs / 1e6
        return f"{hashrate_th:.2f}"

    def __print_device_info(self):
        print(f'\n\n[{self.ip}]')

        print('Temperature:', self.temperature)

        print('MHS av:', self.mhs_av)
        print('MHS 1m:', self.mhs_1m)
        print('MHS 15m:', self.mhs_15m)
        print('Rejected:', self.rejected)

        print('Env Temp:', self.ent_temp)
        print('Chip Temp Avg:', self.chip_temp_avg)
        print('Fan Speed In:', self.fan_speed_in)
        print('Fan Speed Out:', self.fan_speed_out)

        print('Power:', self.power)

        if self.errors:
            for error in self.errors:
                print(f"Str: Device has error code: {error}")
        else:
            print("No error code found")

    # **

    def control(self, token, json_summary, error_msg):
        pass

    # **

    def __apply_asic_data(self, token, json_summary):
        self.ip = token.ip_address
        self.temperature = json_summary['SUMMARY'][0]['Temperature']

        self.mhs_av = self.__convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS av'])
        self.mhs_1m = self.__convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS 1m'])
        self.mhs_15m = self.__convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS 15m'])
        self.rejected = json_summary['SUMMARY'][0]['Rejected']

        self.ent_temp = json_summary['SUMMARY'][0]['Env Temp']
        self.chip_temp_avg = json_summary['SUMMARY'][0]['Chip Temp Avg']
        self.fan_speed_in = json_summary['SUMMARY'][0]['Fan Speed In']
        self.fan_speed_out = json_summary['SUMMARY'][0]['Fan Speed Out']

        self.power = json_summary['SUMMARY'][0]['Power']

    def __apply_asic_errors(self, error_msg):
        if type(error_msg) == str:
            if "error_code" in error_msg:
                error_info = error_msg["error_code"]

                for code in error_info:
                    self.errors.append(code)

        elif type(error_msg) == dict:
            error_info = error_msg.get("error_code", [])

            if error_info:
                for code_info in error_info:
                    for code in code_info:
                        self.errors.append(code)

    def monitor(self):
        for asic_info in self.asics:
            self.tokens.append(WhatsminerAccessToken(
                ip_address=asic_info[0],
                admin_password=asic_info[1]))

        for token in self.tokens:
            json_summary = WhatsminerAPI.get_read_only_info(
                access_token=token,
                cmd="summary")

            error_code_json = WhatsminerAPI.get_read_only_info(
                access_token=token,
                cmd="get_error_code")

            error_msg = error_code_json.get("Msg")

            self.__apply_asic_data(token, json_summary)
            self.__apply_asic_errors(error_msg)

            self.__print_device_info()


# **


class WhatsminerControl:
    pass


# **


asics_list = [
    ('192.168.2.28', 'admin'),
    ('192.168.2.29', 'admin'),
    ('192.168.2.30', 'admin'),
    ('192.168.2.31', 'admin'),
    ('192.168.9.44', 'admin'),
]

monitor = WhatsminerMonitor(asics_list)
monitor.monitor()