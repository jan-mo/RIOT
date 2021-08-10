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
#include <stdlib.h>

#include "shell.h"
#include "msg.h"
#include "board.h"
#include "xtimer.h"
#include "thread.h"

#include "periph/gpio.h"

/* acceleration sensor config */
#include "lis3dh.h"
#define LIS3DH_PARAM_SPI  (SPI_DEV(1))
#define LIS3DH_PARAM_CS   (GPIO_PIN(PA, 17))
#define LIS3DH_PARAM_INT1 (GPIO_PIN(PB, 11))
#define LIS3DH_PARAM_INT2 (GPIO_PIN(PB, 10))
#include "lis3dh_params.h"
static lis3dh_t dev_lis;

/* display PCD8544 */
#include "pcd8544.h"
static pcd8544_t dev_pcd;

/* timings */
#define SECOND          1000000
#define MILLI_SECOND    1000

/* debug config */
#define ENABLE_DEBUG 0
#include "debug.h"

/* ADC config */
#include "periph/adc.h"
#define ADC_SAMPLE_LINE 1   /* PB01 */

/* message queue */
#define MAIN_QUEUE_SIZE (8)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

/* ADC threading */
char adc_thread_stack[THREAD_STACKSIZE_MAIN];
kernel_pid_t ADC_thread_pid;
bool ADC_thread_sleep = false;
uint32_t ADC_thread_delay = 800 * MILLI_SECOND;

/* LIS threading */
char lis_thread_stack[THREAD_STACKSIZE_MAIN];
kernel_pid_t LIS_thread_pid;
bool LIS_thread_sleep = false;
uint32_t LIS_thread_delay = 450 * MILLI_SECOND;

/* toggles the user LED */
static int led_toggle(int argc, char **argv) {
    (void)argc;
    (void)argv;
    LED0_TOGGLE;
    return 1;
}

/* read ADC (differential mode) */
static int adc_read(int argc, char **argv) {
    (void)argc;
    (void)argv;

    ADC_thread_sleep = true;
    char buffer[4] = {0};

    int sample = adc_sample(ADC_LINE(ADC_SAMPLE_LINE), ADC_RES_10BIT);
    DEBUG("ADC value: %d\n", sample);

    /* print to display */
    pcd8544_write_s(&dev_pcd, 0, 0, "ADC: ");
    sprintf(buffer, "%d   ", sample);
    pcd8544_write_s(&dev_pcd, 5, 0, buffer);

    return 1;
}

/* ADC periodic thread */
void *adc_read_periodic(void *arg)
{
    (void) arg;
    int sample = 0;
    char buffer[4] = {0};

    while (1) {
        /* read ADC data */
        sample = adc_sample(ADC_LINE(ADC_SAMPLE_LINE), ADC_RES_10BIT);
        DEBUG("ADC value: %d\n", sample);
        /* print to display */
        pcd8544_write_s(&dev_pcd, 0, 0, "ADC: ");
        sprintf(buffer, "%d   ", sample);
        pcd8544_write_s(&dev_pcd, 5, 0, buffer);

        xtimer_usleep(ADC_thread_delay);
        if (ADC_thread_sleep)
            thread_sleep();
    }

    return NULL;
}

/* ADC wake-up thread */
static int adc_thread_wakeup (int argc, char **argv){
    (void)argc;
    (void)argv;

    ADC_thread_sleep = false;
    thread_wakeup(ADC_thread_pid);

    return 0;
}

/* interrupt callback for user button */
void button_int_cb(void* arg) {
    (void)arg;
    puts("interrupt received.");
}

/* LIS3DH init function */
void lis3dh_func_init(void) {
    if (lis3dh_init(&dev_lis, &lis3dh_params[0]) == 0) {
        puts("lis3dh [Initialized]");
    }
    else {
        puts("lis3dh [Failed]");
    }

    lis3dh_set_odr(&dev_lis, lis3dh_params[0].odr);
    lis3dh_set_scale(&dev_lis, lis3dh_params[0].scale);
    lis3dh_set_axes(&dev_lis, LIS3DH_AXES_XYZ);
}

/* read LIS values */
static int lis3dh_read(int argc, char **argv) {
    (void)argc;
    (void)argv;

    LIS_thread_sleep = true;

    lis3dh_data_t data = {0};
    char buffer[5] = {0};

    lis3dh_read_xyz(&dev_lis, &data);
    DEBUG("X: %d  Y: %d  Z: %d\n", data.acc_x, data.acc_y, data.acc_z);

    /* print to display */
    pcd8544_write_s(&dev_pcd, 0, 1, "X: ");
    sprintf(buffer, "%d    ", data.acc_x);
    pcd8544_write_s(&dev_pcd, 3, 1, buffer);

    pcd8544_write_s(&dev_pcd, 0, 2, "Y: ");
    sprintf(buffer, "%d    ", data.acc_y);
    pcd8544_write_s(&dev_pcd, 3, 2, buffer);

    pcd8544_write_s(&dev_pcd, 0, 3, "Z: ");
    sprintf(buffer, "%d    ", data.acc_z);
    pcd8544_write_s(&dev_pcd, 3, 3, buffer);

    return 0;
}

/* LIS periodic thread */
void *lis_read_periodic(void *arg)
{
    (void) arg;
    lis3dh_data_t data = {0};
    char buffer[5] = {0};

    while (1) {
        /* read LIS data */
        lis3dh_read_xyz(&dev_lis, &data);
        DEBUG("X: %d  Y: %d  Z: %d\n", data.acc_x, data.acc_y, data.acc_z);

        /* print to display */
        pcd8544_write_s(&dev_pcd, 0, 1, "X: ");
        sprintf(buffer, "%d    ", data.acc_x);
        pcd8544_write_s(&dev_pcd, 3, 1, buffer);

        pcd8544_write_s(&dev_pcd, 0, 2, "Y: ");
        sprintf(buffer, "%d    ", data.acc_y);
        pcd8544_write_s(&dev_pcd, 3, 2, buffer);

        pcd8544_write_s(&dev_pcd, 0, 3, "Z: ");
        sprintf(buffer, "%d    ", data.acc_z);
        pcd8544_write_s(&dev_pcd, 3, 3, buffer);

        xtimer_usleep(LIS_thread_delay);
        if (LIS_thread_sleep)
            thread_sleep();
    }

    return NULL;
}

/* LIS wake-up thread */
static int lis_thread_wakeup (int argc, char **argv){
    (void)argc;
    (void)argv;

    LIS_thread_sleep = false;
    thread_wakeup(LIS_thread_pid);

    return 0;
}

/* turn on the display */
static int display_on(int argc, char **argv) {
    (void)argc;
    (void)argv;

    pcd8544_poweron(&dev_pcd);
    return 0;
}

/* turn off the display */
static int display_off(int argc, char **argv) {
    (void)argc;
    (void)argv;

    pcd8544_poweroff(&dev_pcd);
    return 0;
}

/* clear the display content */
static int display_clear(int argc, char **argv) {
    (void)argc;
    (void)argv;

    pcd8544_clear(&dev_pcd);
    return 0;
}

/* display riot-logo */
static int display_riot(int argc, char **argv) {
    (void)argc;
    (void)argv;

    pcd8544_riot(&dev_pcd);
    return 0;
}

/* invert display content */
static int display_invert(int argc, char **argv) {
    (void)argc;
    (void)argv;

    pcd8544_invert(&dev_pcd);
    return 0;
}

/* write to specific line and column of display */
static int display_write(int argc, char **argv) {
    uint8_t x, y;

    if (argc < 4) {
        printf("usage: %s LINE COLUMN STRING\n", argv[0]);
        return -1;
    }

    x = atoi(argv[1]);
    y = atoi(argv[2]);

    pcd8544_write_s(&dev_pcd, y, x, argv[3]);
    return 0;
}

/* shell commands */
static const shell_command_t shell_commands[] = {
    { "disp_on", "Turn on the display", display_on },
    { "disp_off", "Turn off the display", display_off },
    { "disp_riot", "Displays RIOT logo", display_riot },
    { "disp_invert", "Invert display", display_invert },
    { "disp_write", "Write string to display", display_write},
    { "disp_clear", "Clear display", display_clear },
    { "lis_read", "Read acceleration data", lis3dh_read },
    { "lis_read_periodic", "Periodic read of acceleration data", lis_thread_wakeup },
    { "adc_read", "Read ADC value, stops periodic read", adc_read},
    { "adc_read_periodic", "Periodic read of ADC value", adc_thread_wakeup},
    { "led_toggle", "Toggles the LED0 status", led_toggle},
    { NULL, NULL, NULL }
};


int main(void) {

    puts("Example Firmware");

    printf("You are running RIOT on a(n) %s board.\n", RIOT_BOARD);
    printf("This board features a(n) %s MCU.\n", RIOT_MCU);

    /* power off the LED */
    LED0_OFF;

    /* setting up interrupt pin (user button) */
    gpio_init_int(BTN0_PIN, BTN0_MODE, GPIO_FALLING, button_int_cb, NULL);
    gpio_irq_enable(BTN0_PIN);

    /* setting up ADC */
    adc_init(ADC_LINE(ADC_SAMPLE_LINE));
    /* starting sleeping ADC thread */
    ADC_thread_pid = thread_create( adc_thread_stack, sizeof(adc_thread_stack),
                        THREAD_PRIORITY_MAIN - 1, THREAD_CREATE_SLEEPING,
                        adc_read_periodic, NULL, "ADC_periodic");

    /* initializes the message queue */
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);

    /* initializes acceleration sensor */
    lis3dh_func_init();
    /* starting sleeping LIS thread */
    LIS_thread_pid = thread_create( lis_thread_stack, sizeof(lis_thread_stack),
                        THREAD_PRIORITY_MAIN - 1, THREAD_CREATE_SLEEPING,
                        lis_read_periodic, NULL, "LIS_periodic");

    printf("Initializing PCD8544 LCD at SPI_%i...\n", SPI_DEV(0));
    if (pcd8544_init(&dev_pcd, SPI_DEV(0), GPIO_PIN(PA,5),
                     GPIO_PIN(PB,9), GPIO_PIN(PB,8)) != 0) {
        puts("Failed to initialize PCD8544 display");
        return 1;
    }

    /* display riot-logo for one second */
    pcd8544_clear(&dev_pcd);
    pcd8544_poweron(&dev_pcd);
    pcd8544_riot(&dev_pcd);
    xtimer_usleep(1 * SECOND);
    pcd8544_clear(&dev_pcd);
    pcd8544_write_s(&dev_pcd, 3, 1, "Running");
    pcd8544_write_s(&dev_pcd, 3, 2, "Example");
    pcd8544_write_s(&dev_pcd, 3, 3, "Firmware");
    xtimer_usleep(2 * SECOND);
    pcd8544_clear(&dev_pcd);

    /* start shell */
    puts("All up, running the shell now");
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(shell_commands, line_buf, SHELL_DEFAULT_BUFSIZE);

    /* should be never reached */
    return 0;
}
