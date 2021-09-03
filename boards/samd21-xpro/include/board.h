/*
 * Copyright (C) 2017 Travis Griggs <travisgriggs@gmail.com>
 * Copyright (C) 2017 Dan Evans <photonthunder@gmail.com>
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     boards_samd21-xpro
 * @{
 *
 * @file
 * @brief       Board specific definitions for the Atmel SAM D21 Xplained Pro
 *              board
 *
 * @author      Travis Griggs <travisgriggs@gmail.com>
 * @author      Dan Evans <photonthunder@gmail.com>
 * @author      Sebastian Meiling <s@mlng.net>
 */

#ifndef BOARD_H
#define BOARD_H

#include "cpu.h"
#include "periph_conf.h"
#include "periph_cpu.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @name    xtimer configuration
 * @{
 */
#define XTIMER_DEV          TIMER_DEV(1)
#define XTIMER_CHAN         (0)
/** @} */

/**
 * @name   LED pin definitions and handlers
 * @{
 */
#define LED0_PIN            GPIO_PIN(PB, 30)

#define LED_PORT            PORT->Group[PB]
#define LED0_MASK           (1 << 30)

#define LED0_ON             (LED_PORT.OUTCLR.reg = LED0_MASK)
#define LED0_OFF            (LED_PORT.OUTSET.reg = LED0_MASK)
#define LED0_TOGGLE         (LED_PORT.OUTTGL.reg = LED0_MASK)
/** @} */

/**
 * @name SW0 (Button) pin definitions
 * @{
 */
#define BTN0_PORT           PORT->Group[PA]
#define BTN0_PIN            GPIO_PIN(PA, 15)
#define BTN0_MODE           GPIO_IN_PU
/** @} */

/**
 * @name LIS acceleration pin definitions
 * @{
 */
 #ifdef MODULE_LIS2DH12_SPI
    #define LIS2DH12_PARAM_SPI  SPI_DEV(1)
    #define LIS2DH12_PARAM_CS   GPIO_PIN(PA, 17)
#elif MODULE_LIS3DH
    #define LIS3DH_PARAM_SPI    SPI_DEV(1)
    #define LIS3DH_PARAM_CS     GPIO_PIN(PA, 17)
    #define LIS3DH_PARAM_INT1   GPIO_PIN(PB, 11)
    #define LIS3DH_PARAM_INT2   GPIO_PIN(PB, 10)
#endif
/** @} */

/**
 * @name WIFI WINC1500 pin definitions
 * @{
 */
#define ATWINC15X0_PARAM_SPI            (SPI_DEV(2))
#define ATWINC15X0_PARAM_RESET_PIN      (GPIO_PIN(PB, 30))
#define ATWINC15X0_PARAM_WAKE_PIN       (GPIO_PIN(PA, 15))
#define ATWINC15X0_PARAM_IRQ_PIN        (GPIO_PIN(PA, 28))
#define ATWINC15X0_PARAM_CHIP_EN_PIN    (GPIO_PIN(PA, 27))
#define ATWINC15X0_PARAM_SSN_PIN        (GPIO_PIN(PB, 17))
/** @} */

/**
 * @brief Initialize board specific hardware, including clock, LEDs and std-IO
 */
void board_init(void);

#ifdef __cplusplus
}
#endif

#endif /* BOARD_H */
/** @} */
