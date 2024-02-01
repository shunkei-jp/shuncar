cmake_minimum_required(VERSION 3.13)

# initialize the SDK based on PICO_SDK_PATH
# note: this must happen before project()
include(pico_sdk_import.cmake)

project(shuncar_pico)

pico_sdk_init()

add_executable(shuncar_pico main.c)

# pull in common dependencies
target_link_libraries(shuncar_pico pico_stdlib hardware_pwm hardware_adc)
#target_link_libraries(main pico_stdlib)

# create map/bin/hex file etc.
pico_add_extra_outputs(shuncar_pico)

# add url via pico_set_program_url
#example_auto_set_url(hello_uart)

pico_enable_stdio_usb(shuncar_pico 1)
pico_enable_stdio_uart(shuncar_pico 0)

# target_compile_definitions(main PRIVATE
# # PICO_DEFAULT_UART_TX_PIN=16
# # PICO_DEFAULT_UART_RX_PIN=17
# PICO_DEFAULT_UART_TX_PIN=12
# PICO_DEFAULT_UART_RX_PIN=13
# )
