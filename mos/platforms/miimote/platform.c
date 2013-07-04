/*
 * Copyright (c) 2013, Institute of Electronics and Computer Science
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *  * Redistributions of source code must retain the above copyright notice,
 *    this list of  conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

//----------------------------------------------------------
//      Platform code
//----------------------------------------------------------
#include "platform.h"
#include <digital.h>
#include <serial_number.h>


#define XREN(port) P##port##REN
#define REN(port)  XREN(port)

//----------------------------------------------------------
//      Init the platform as if on cold reset
//----------------------------------------------------------
void initPlatform(void)
{
    msp430Init();

    // Switch the UART/SDA-12 line to UART mode
    pinAsOutput(1, 0);
    pinClear(1, 0);

#if USE_ADC
    // TODO: 1.5V or 2.5V ?
    hplAdcUse2V5VRef(); // Soil humidity sensor outputs ~0--2.5 V
    //ADC10AE1 |= BV(SOIL_HUMIDITY_AE_BIT);
#endif

#if USE_SERIAL_NUMBER
    // Set up Vcc for the DS2411
    pinAsOutput(DS2411_VCC_PORT, DS2411_VCC_PIN);
    pinSet(DS2411_VCC_PORT, DS2411_VCC_PIN);

    // Enable the pullup resistor
    REN(DS2411_PORT) |= BV(DS2411_PIN);

    // Read the serial number
    serialNumberInit();

    // Disable Vcc
    pinClear(DS2411_VCC_PORT, DS2411_VCC_PIN);
#endif
}