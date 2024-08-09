from whatsminer import WhatsminerAccessToken, WhatsminerAPI


class WhatsminerCollectData:
    def __init__(self, asics):
        self.asics = asics
        self.tokens = []
        self.asics_detail = {}

    @classmethod
    def __convert_mhs_to_th_str(cls, mhs):
        hashrate_th = mhs / 1e6
        return f"{hashrate_th:.2f}"

    def __write_data(self, token, json_summary, json_pool, error_msg):
        ip = token.ip_address

        temperature = json_summary['SUMMARY'][0]['Temperature']

        mhs_av = self.__convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS av'])
        mhs_1m = self.__convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS 1m'])
        mhs_15m = self.__convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS 15m'])
        rejected = json_summary['SUMMARY'][0]['Rejected']
        env_temp = json_summary['SUMMARY'][0].get('Env Temp', 0)
        
        fan_speed_in = json_summary['SUMMARY'][0]['Fan Speed In']
        fan_speed_out = json_summary['SUMMARY'][0]['Fan Speed Out']

        pools_worker_name = json_pool['POOLS'][0]['User']

        factory_ghs = json_summary['SUMMARY'][0]['Factory GHS']
        power = json_summary['SUMMARY'][0]['Power']
        uptime = json_summary['SUMMARY'][0]['Uptime']

        # **

        asic_data = {
            'token': token,
            'temperature': temperature,
            'mhs_av': mhs_av,
            'mhs_1m': mhs_1m,
            'mhs_15m': mhs_15m,
            'rejected': rejected,
            'env_temp': env_temp,
            'fan_speed_in': fan_speed_in,
            'fan_speed_out': fan_speed_out,
            'power': power,

            'pools_worker_name': pools_worker_name,
            'factory_ghs': factory_ghs,
            'uptime': uptime,

            'errors': []
        }

        # **

        if ip not in self.asics_detail:
            self.asics_detail[ip] = []

        self.asics_detail[ip].append(asic_data)
        self.__write_errors(error_msg, ip)

    def __write_errors(self, error_msg, ip):
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

    def collect_data(self):
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

            self.__write_data(token, json_summary, json_pool, error_msg)

    def get_data(self):
        return self.asics_detail
