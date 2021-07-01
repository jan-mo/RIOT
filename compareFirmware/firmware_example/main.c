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

#define MAIN_QUEUE_SIZE     (8)
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
    int sample = adc_sample(ADC_LINE(0), ADC_RES_10BIT);
    printf("ADC value: %d\n", sample);
    return 1;
}

/* interrupt callback for user button */
void button_int_cb(void* arg){
    (void)arg;
    puts("interrupt received.");
}

/* shell commands */
static const shell_command_t shell_commands[] = {
    { "toggle_LED", "toggles the LED status of LED0", toggle_LED},
    { "adc", "reads the ADC0", read_ADC},
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
    adc_init(ADC_LINE(0));

    /* initializes the message queue */
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);

    /* start shell */
    puts("All up, running the shell now");
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(shell_commands, line_buf, SHELL_DEFAULT_BUFSIZE);

    /* should be never reached */
    return 0;
}
