#include "hardware/adc.h"
#include "hardware/clocks.h"
#include "hardware/pwm.h"
#include "hardware/uart.h"
#include "pico/stdlib.h"
#include <stdio.h>

#define STEER_IDLE 95
#define THROTTLE_IDLE 90

#define BRAKE_PWM 105
#define BRAKE_TIME 1000
#define BRAKE_THRESHOLD 88

#define NO_SIGNAL_TIMEOUT 100
#define NO_XBEE_TIMEOUT 100

#define PWM_THROTTLE_PIN 16
#define PWM_STEERING_PIN 17

#define BATT_ADC_PIN 28
#define BATT_ADC_ADC 2

// #define XBEE_ENABLE

#ifdef XBEE_ENABLE
#define XBEE_UART uart0
#define XBEE_UART_TX_PIN 12
#define XBEE_UART_RX_PIN 13
#endif

#define CTRL_UART uart0
#define CTRL_UART_TX_PIN 0
#define CTRL_UART_RX_PIN 1

#define NOEMERG_JUMPER_PIN 14

#define LED_PIN PICO_DEFAULT_LED_PIN
#define LED_BRINK_PERIOD 300
#define LED_BRINK_ON_TIME 150

int main() {
  stdio_init_all();

  gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

  gpio_init(NOEMERG_JUMPER_PIN);
  gpio_set_dir(NOEMERG_JUMPER_PIN, GPIO_IN);

  gpio_set_function(PWM_THROTTLE_PIN, GPIO_FUNC_PWM);
  gpio_set_function(PWM_STEERING_PIN, GPIO_FUNC_PWM);

#ifdef XBEE_ENABLE
  gpio_set_function(XBEE_UART_TX_PIN, GPIO_FUNC_UART);
  gpio_set_function(XBEE_UART_RX_PIN, GPIO_FUNC_UART);
  uart_init(XBEE_UART, 9600);
#endif

  gpio_set_function(CTRL_UART_TX_PIN, GPIO_FUNC_UART);
  gpio_set_function(CTRL_UART_RX_PIN, GPIO_FUNC_UART);
  uart_init(CTRL_UART, 115200);

  int pwm_slice_throttle = pwm_gpio_to_slice_num(PWM_THROTTLE_PIN);
  int pwm_slice_steering = pwm_gpio_to_slice_num(PWM_STEERING_PIN);

  int pwm_chan_throttle = pwm_gpio_to_channel(PWM_THROTTLE_PIN);
  int pwm_chan_steering = pwm_gpio_to_channel(PWM_STEERING_PIN);

  // init pwm
  pwm_set_wrap(pwm_slice_throttle, 16666);
  pwm_set_clkdiv(pwm_slice_throttle, 125.0);
  pwm_set_chan_level(pwm_slice_throttle, pwm_chan_throttle, 1000);
  pwm_set_enabled(pwm_slice_throttle, true);

  pwm_set_wrap(pwm_slice_steering, 16666);
  pwm_set_clkdiv(pwm_slice_steering, 125.0);
  pwm_set_chan_level(pwm_slice_steering, pwm_chan_steering, 3000);
  pwm_set_enabled(pwm_slice_steering, true);

  // intialize adc
  adc_init();
  adc_gpio_init(BATT_ADC_PIN);
  adc_select_input(BATT_ADC_ADC);

  // Send out a character without any conversions
  char buf[100];
  int buf_ptr = 0;
  uint32_t control_last_received = 0;
  uint32_t xbee_last_received = 0;
  uint32_t keepalive_last_sent = 0;
  int steer_pwm = STEER_IDLE;
  int throttle_pwm = THROTTLE_IDLE;
  bool emg_stop_armed = false;
  bool emg_stop_armed_prev = false;
  bool brake_triggerd = false;
  bool available = false;
  uint32_t brake_start = 0;

  while (1) {
    available = true;
    if (uart_is_readable(CTRL_UART)) {
      char c = uart_getc(CTRL_UART);
      printf("%c", c);
      if (c == '\n' || c == '\r') {
        buf[buf_ptr] = '\0';
        buf_ptr = 0;

        unsigned long steer, throttle;
        int n = sscanf(buf, "%lu %lu", &steer, &throttle);
        if (n == 2) {
          steer_pwm = steer;
          throttle_pwm = throttle;
          control_last_received = to_ms_since_boot(get_absolute_time());
        }
      } else {
        buf[buf_ptr] = c;
        buf_ptr++;
        if (buf_ptr >= 100) {
          buf_ptr = 0;
        }
      }
    }

    if (to_ms_since_boot(get_absolute_time()) - control_last_received >
        NO_SIGNAL_TIMEOUT) {
      available = false;
      steer_pwm = STEER_IDLE;
      throttle_pwm = THROTTLE_IDLE;
    }

#ifdef XBEE_ENABLE
    if (uart_is_readable(XBEE_UART)) {
      char c = uart_getc(XBEE_UART);
      uart_putc(XBEE_UART, c);
      printf("%c", c);
      if (c == 'k') {
        xbee_last_received = to_ms_since_boot(get_absolute_time());
        printf("keep\n\r");
      }
    }

    if (gpio_get(NOEMERG_JUMPER_PIN) &&
        (to_ms_since_boot(get_absolute_time()) - xbee_last_received >
         NO_XBEE_TIMEOUT)) {
      emg_stop_armed = true;
    } else {
      emg_stop_armed = false;
    }
#else
    emg_stop_armed = false;
#endif

    if (emg_stop_armed && !emg_stop_armed_prev) {
      if (throttle_pwm < BRAKE_THRESHOLD) {
        brake_triggerd = true;
        brake_start = to_ms_since_boot(get_absolute_time());
      }
    }

    emg_stop_armed_prev = emg_stop_armed;

    if (emg_stop_armed) {
      available = false;
      steer_pwm = STEER_IDLE;
      throttle_pwm = THROTTLE_IDLE;
    }

    if (available &&
        to_ms_since_boot(get_absolute_time()) - keepalive_last_sent > 100) {
      keepalive_last_sent = to_ms_since_boot(get_absolute_time());
      uart_putc(CTRL_UART, 'k');
      uart_putc(CTRL_UART, '\n');

      // read battery voltage
      uint16_t batt_raw = adc_read();
      float batt_pin_volt = batt_raw * 3.3 / 4096.0;
      float batt_volt = batt_pin_volt * 10.2 / 2.0;
      char buf[100];
      sprintf(buf, "batt: %f\n\r", batt_volt);
      uart_puts(CTRL_UART, buf);
    }

    if (brake_triggerd) {
      if (to_ms_since_boot(get_absolute_time()) - brake_start > BRAKE_TIME) {
        brake_triggerd = false;
      } else {
        throttle_pwm = BRAKE_PWM;
      }
    }

    // control led
    if (to_ms_since_boot(get_absolute_time()) % LED_BRINK_PERIOD <
        LED_BRINK_ON_TIME) {
      gpio_put(LED_PIN, 1);
    } else {
      if (!emg_stop_armed) {
        gpio_put(LED_PIN, 1);
      } else {
        gpio_put(LED_PIN, 0);
      }
    }

    // update pwm
    pwm_set_chan_level(pwm_slice_throttle, pwm_chan_throttle,
                       throttle_pwm * 16666 / 1000);
    pwm_set_chan_level(pwm_slice_steering, pwm_chan_steering,
                       steer_pwm * 16666 / 1000);
  }
}
