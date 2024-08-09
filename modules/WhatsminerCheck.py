from whatsminer import WhatsminerAccessToken, WhatsminerAPI
from modules.AsicStatusInterface import AsicStatusInterface


# **


class WhatsminerCheck(AsicStatusInterface):
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

            return WhatsminerCheck.__check_is_asic(token, json_summary)
        except Exception as e:
            return False
