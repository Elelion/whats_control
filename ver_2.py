from whatsminer import WhatsminerAccessToken, WhatsminerAPI

asics = [
    ('192.168.2.28', 'admin'),
    ('192.168.2.29', 'admin'),
    ('192.168.2.30', 'admin'),
    ('192.168.2.31', 'admin'),
    ('192.168.9.44', 'admin'),
]
tokens = []


# -----------------------------------------------------------------------------


def convert_mhs_to_th_str(mhs):
    hashrate_th = mhs / 1e6
    return f"{hashrate_th:.2f}"


# -----------------------------------------------------------------------------


for asic_info in asics:
    tokens.append(WhatsminerAccessToken(ip_address=asic_info[0], admin_password=asic_info[1]))

# Find machines running too hot
for token in tokens:

    # JSON -> "cmd":"summary"
    # Return -> SUMMARY: [{Temperature, ...}]
    json_summary = WhatsminerAPI.get_read_only_info(access_token=token, cmd="summary")

    print(f'\n\n[{token.ip_address}]')

    print('Temperature', json_summary['SUMMARY'][0]['Temperature'])

    print('MHS av:', convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS av']))
    print('MHS 1m:', convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS 1m']))
    print('MHS 15m:', convert_mhs_to_th_str(json_summary['SUMMARY'][0]['MHS 15m']))
    print('Rejected:', json_summary['SUMMARY'][0]['Rejected'])

    print('Env Temp:', json_summary['SUMMARY'][0]['Env Temp'])
    print('Chip Temp Avg:', json_summary['SUMMARY'][0]['Chip Temp Avg'])
    print('Fan Speed In:', json_summary['SUMMARY'][0]['Fan Speed In'])
    print('Fan Speed Out:', json_summary['SUMMARY'][0]['Fan Speed Out'])

    print('Power:', json_summary['SUMMARY'][0]['Power'])

    # **

    error_code_json = WhatsminerAPI.get_read_only_info(access_token=token, cmd="get_error_code")
    error_msg = error_code_json.get("Msg")


    print("Errors type", type(error_msg))

    if type(error_msg) == str:
        if "error_code" in error_msg:
            error_info = error_msg["error_code"]

            for code in error_info.items():
                print(f"Str: Device has error code: {code}")
        else:
            print("Str: No error code found.")

    elif type(error_msg) == dict:
        # for code in error_msg:
        #     print(f"Device has error code: {code}")
        error_msg = error_code_json.get("Msg", {})
        error_info = error_msg.get("error_code", [])

        if error_info:
            for code_info in error_info:
                for code in code_info:
                    print(f"Dict: Device has error code: {code}")
        else:
            print("Dict: No error code found.")
