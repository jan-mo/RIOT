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

/* acceleration sensor */
#include "lis3dh.h"
/* define LIS3DH params */
#define LIS3DH_PARAM_SPI  (SPI_DEV(1))
#define LIS3DH_PARAM_CS   (GPIO_PIN(PA, 17))
#define LIS3DH_PARAM_INT1 (GPIO_PIN(PB, 11))
#define LIS3DH_PARAM_INT2 (GPIO_PIN(PB, 10))
#include "lis3dh_params.h"

static lis3dh_t dev;

#define ENABLE_DEBUG 0
#include "debug.h"

#define ADC_SAMPLE_LINE 1

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

/* LIS3DH init function */
void lis3dh_func_init(void) {

    /* init lis */
    if (lis3dh_init(&dev, &lis3dh_params[0]) == 0) {
        puts("lis3dh [Initialized]");
    }
    else {
        puts("lis3dh [Failed]");
    }

    lis3dh_set_odr(&dev, lis3dh_params[0].odr);
    lis3dh_set_scale(&dev, lis3dh_params[0].scale);
    lis3dh_set_axes(&dev, LIS3DH_AXES_XYZ);

}

/* read LIS values */
static int lis3dh_read(int argc, char **argv)
{
    (void)argc;
    (void)argv;

    lis3dh_data_t data;

    lis3dh_read_xyz(&dev, &data);

    printf("X: %d  Y: %d  Z: %d\n", data.acc_x, data.acc_y, data.acc_z);

    return 0;
}

/* shell commands */
static const shell_command_t shell_commands[] = {
    { "toggle_LED", "toggles the LED status of LED0", toggle_LED },
    { "adc", "reads the ADC0", read_ADC },
    { "lis_read", "Read acceleration data", lis3dh_read },
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
    lis3dh_func_init();

    /* start shell */
    puts("All up, running the shell now");
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(shell_commands, line_buf, SHELL_DEFAULT_BUFSIZE);

    /* should be never reached */
    return 0;
}
