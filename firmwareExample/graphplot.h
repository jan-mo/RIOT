/*
 * Copyright (C) 2021 Technische Universität Berlin
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     firmwareExample
 * @brief       Module to plot a graph on LCD display PCD8544
 *
 * @{
 *
 * @file
 * @brief       Interface definition for plotting on the PCD8544 LCD
 *
 * @author      Jan Mohr <jan.mohr@campus.tu-berlin.de>
 */

#ifndef GRAPHPLOT_H
#define GRAPHPLOT_H

#include <stdint.h>

#include "pcd8544.h"

#define GRAPHPLOT_OFFSET_X 3
#define GRAPHPLOT_OFFSET_Y 3

#ifdef __cplusplus
 extern "C" {
#endif

/**
 * @brief   Sets a single pixel on the display
 *
 * The position of the pixel is specified in columns (x) and rows (y)
 *
 * @param[in] dev       device descriptor of display to use
 * @param[in] x         column_px absolute position to write pixel [0 - 83]
 * @param[in] y         row_px absolute position to write pixel [0 - 47]
 */
void graphplot_write_pixel(const pcd8544_t *dev, uint8_t x, uint8_t y);

/**
 * @brief   Removes a single pixel on the display
 *
 * The position of the pixel is specified in columns (x) and rows (y)
 *
 * @param[in] dev       device descriptor of display to use
 * @param[in] x         column_px absolute position to clear pixel [0 - 83]
 * @param[in] y         row_px absolute position to clear pixel [0 - 47]
 */
void graphplot_clear_pixel(const pcd8544_t *dev, uint8_t x, uint8_t y);

/**
 * @brief   Write the diagram-image to memory of the given display
 *
 * The diagram-image is displayed after calling the function and the
 * pixel array is updated.
 *
 * @param[in] dev       device descriptor of display to use
 * @param[in] mode      set the mode of the diagram [0 - 1]
 */
void graphplot_diagram(const pcd8544_t *dev, uint8_t mode);

/**
 * @brief   Set the min and max value for y-axis
 *
 * The min and max of the graph can be set,
 * needs for graphplot_write_coordinate() function
 *
 * @param[in] dev       device descriptor of display to use
 * @param[in] min       the minimum value for y-axis
 * @param[in] max       the maximum value for y-axis
 */
void graphplot_set_min_max(int16_t min, int16_t max);

/**
 * @brief   Write coordinate to the graph
 *
 * The position of the pixel is calculated with min max value of the graph,
 * function graphplot_set_min_max() needs to be called before 
 *
 * @param[in] dev           device descriptor of display to use
 * @param[in] x_coordinate  time_tick value of the graph [0 - 83]
 * @param[in] y_coordinate  value must be between min max, can be raw data value
 */
void graphplot_write_coordinate(const pcd8544_t *dev, uint8_t x_coordinate, int16_t y_coordinate);

/**
 * @brief   Clear the pixel array
 *
 * The pixel array is set to zero
 *
 */
void graphplot_clear(void);

#ifdef __cplusplus
}
#endif

#endif /* GRAPHPLOT_H */
/** @} */
