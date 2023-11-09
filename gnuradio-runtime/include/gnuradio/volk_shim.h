/* -*- c++ -*- */
/*
 * Copyright 2023 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#ifndef INCLUDED_GR_RUNTIME_VOLK_SHIM_H
#define INCLUDED_GR_RUNTIME_VOLK_SHIM_H

#include <gnuradio/api.h>
#include <volk/volk.h>

#ifdef __cplusplus
extern "C" {
#endif

GR_RUNTIME_API void volk_32fc_s32fc_x2_rotator_32fc_shim(lv_32fc_t* outVector,
                                                         const lv_32fc_t* inVector,
                                                         const lv_32fc_t* phase_inc,
                                                         lv_32fc_t* phase,
                                                         unsigned int num_points);

GR_RUNTIME_API void volk_32fc_s32fc_multiply_32fc_shim(lv_32fc_t* cVector,
                                                       const lv_32fc_t* aVector,
                                                       const lv_32fc_t* scalar,
                                                       unsigned int num_points);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDED_GR_RUNTIME_VOLK_SHIM_H */
