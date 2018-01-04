# globals 
#import socket

# bill related globals - used to calculate credit & co.
bill_settings = []
bill_expansion = []
bill_stacker = 0 # current number of bills in stacker 
bill_poll_response = []
bill_inited = False
bill_level = 0
bill_scaling_factor = 0
bill_value = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
bill_decimal_places = 0
bill_stacker_cappacity = 0
bill_recycling_option = False
bill_timeout = 0.001
bill_previous_status = 0x00

# coin related globals - used to calculate credit & Co.
coin_settings = []
coin_expansion = []
coin_tube_status = 0 # current value of coins in tubes
coin_poll_response = []
coin_inited = False
coin_level = 0
coin_scaling_factor = 0
coin_value = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
coin_routing_channel = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
coin_decimal_places = 0
coin_alternative_payout = False
coin_timeout = 0.001
coin_previous_status = 0x00

# VMC data for cashless init
vmc_level = 0x02
vmc_display_columns = 0x00
vmc_display_rows = 0x00
vmc_display_info = 0x00
vmc_manufacturer_code = "ATM"
vmc_serial_number = "000000000001"
vmc_model_number =  "RASPIVENDDIR"
vmc_software_version = [0x01,0x01]

# cashless #1 related globals - used to calculate credit & co.
cashless1_settings = []
cashless1_expansion = []
cashless1_poll_response = []
cashless1_inited = False
cashless1_level = 0
cashless1_scaling_factor = 0
cashless1_decimal_places = 0
cashless1_timeout = 0.001
cashless1_previous_status = 0x00
cashless1_maximum_response_time = 0xFF
cashless1_revalue = False
cashless1_multivend = False
cashless1_has_display = False
cashless1_session_active = False
cashless1_revalue_limit = 0

# cashless #2 related globals - used to calculate credit & co.
cashless2_settings = []
cashless2_expansion = []
cashless2_poll_response = []
cashless2_inited = False
cashless2_level = 0
cashless2_scaling_factor = 0
cashless2_decimal_places = 0
cashless2_timeout = 0.001
cashless2_previous_status = 0x00
cashless2_maximum_response_time = 0xFF
cashless2_revalue = False
cashless2_multivend = False
cashless2_has_display = False
cashless2_session_active = False
cashless2_revalue_limit = 0
