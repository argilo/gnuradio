/* -*- c -*- */
/*
 * Copyright 2023 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include <gnuradio/volk_shim.h>

void volk_32fc_s32fc_x2_rotator_32fc_shim(lv_32fc_t* outVector,
                                          const lv_32fc_t* inVector,
                                          const lv_32fc_t* phase_inc,
                                          lv_32fc_t* phase,
                                          unsigned int num_points)
{
    volk_32fc_s32fc_x2_rotator_32fc(outVector, inVector, *phase_inc, phase, num_points);
}

void volk_32fc_s32fc_multiply_32fc_shim(lv_32fc_t* cVector,
                                        const lv_32fc_t* aVector,
                                        const lv_32fc_t* scalar,
                                        unsigned int num_points)
{
    volk_32fc_s32fc_multiply_32fc(cVector, aVector, *scalar, num_points);
}
