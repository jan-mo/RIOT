/*
 * Copyright (C) 2021 Technische Universität Berlin
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     examples
 * @{
 *
 * @file
 * @brief       Example Firmware
 *
 * @author      Jan Mohr <jan.mohr@campus.tu-berlin.de>
 *
 * @}
 */

#include <stdio.h>

#include "shell.h"
#include "msg.h"
#include "periph/gpio.h"
#include "periph/adc.h"
#include "board.h"

/* LIS2DH12 */
#define LIS2DH12_PARAM_SPI  SPI_DEV(2)
#define LIS2DH12_PARAM_CS   GPIO_PIN(PB, 17)
#include "lis2dh12.h"
#include "lis2dh12_params.h"
#include "lis2dh12_registers.h"
/* allocate device descriptor */
static lis2dh12_t dev;


#define ENABLE_DEBUG 0
#include "debug.h"

#define ADC_SAMPLE_LINE 0

#define MAIN_QUEUE_SIZE (8)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

/* toggles the user LED */
static int toggle_LED(int argc, char **argv){
    (void)argc;
    (void)argv;
    LED0_TOGGLE;
    return 1;
}

/* read ADC (differential mode) */
static int read_ADC(int argc, char **argv){
    (void)argc;
    (void)argv;
    int sample = adc_sample(ADC_LINE(ADC_SAMPLE_LINE), ADC_RES_10BIT);
    printf("ADC value: %d\n", sample);
    return 1;
}

/* interrupt callback for user button */
void button_int_cb(void* arg){
    (void)arg;
    puts("interrupt received.");
}

/* LIS2DH12 init function */
void lis2dh12_test_init(void) {

    if (IS_USED(MODULE_LIS2DH12_SPI)) {
        puts("using SPI mode, for I2C mode select the lis2dh12_i2c module");
    } else {
        puts("using I2C mode, for SPI mode select the lis2dh12_spi module");
    }

    /* init lis */
    if (lis2dh12_init(&dev, &lis2dh12_params[0]) == LIS2DH12_OK) {
        puts("lis2dh12 [Initialized]");
    }
    else {
        puts("lis2dh12 [Failed]");
    }

    /* change LIS settings */
    lis2dh12_set_powermode(&dev, LIS2DH12_POWER_LOW);
    lis2dh12_set_datarate(&dev, LIS2DH12_RATE_100HZ);
    lis2dh12_set_scale(&dev, LIS2DH12_SCALE_2G);

    /* configure FIFO */
    lis2dh12_fifo_t fifo_cfg = {
        .FIFO_mode = LIS2DH12_FIFO_MODE_STREAM,
    };

    lis2dh12_set_fifo(&dev, &fifo_cfg);
}

/* read LIS values */
static int shell_is2dh12_read(int argc, char **argv)
{
    (void)argc;
    (void)argv;

    int16_t data[3] = {0};

    lis2dh12_read(&dev, data);

    printf("X: %d  Y: %d  Z: %d\n", data[0], data[1], data[2]);

    return 0;
}

/* shell commands */
static const shell_command_t shell_commands[] = {
    { "toggle_LED", "toggles the LED status of LED0", toggle_LED },
    { "adc", "reads the ADC0", read_ADC },
    { "lis_read", "Read acceleration data", shell_is2dh12_read },
    { NULL, NULL, NULL }
};

int main(void)
{
    puts("Example Firmware");

    printf("You are running RIOT on a(n) %s board.\n", RIOT_BOARD);
    printf("This board features a(n) %s MCU.\n", RIOT_MCU);

    /* powers off the LED */
    LED0_OFF;

    /* setting up interrupt pin (user button) */
    gpio_init_int(BTN0_PIN, BTN0_MODE, GPIO_FALLING, button_int_cb, NULL);
    gpio_irq_enable(BTN0_PIN);

    /* setting up ADC */
    adc_init(ADC_LINE(ADC_SAMPLE_LINE));

    /* initializes the message queue */
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);

    /* init acceleration sensor */
    lis2dh12_test_init();

    /* start shell */
    puts("All up, running the shell now");
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(shell_commands, line_buf, SHELL_DEFAULT_BUFSIZE);

    /* should be never reached */
    return 0;
}
