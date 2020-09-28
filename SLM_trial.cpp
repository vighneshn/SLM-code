/************************ \cond COPYRIGHT *****************************
 *                                                                    *
 * Copyright (C) 2020 HOLOEYE Photonics AG. All rights reserved.      *
 * Contact: https://holoeye.com/contact/                              *
 *                                                                    *
 * This file is part of HOLOEYE SLM Display SDK.                      *
 *                                                                    *
 * You may use this file under the terms and conditions of the        *
 * "HOLOEYE SLM Display SDK Standard License v1.0" license agreement. *
 *                                                                    *
 **************************** \endcond ********************************/


 // Calculates a lens using numpy and show it on the SLM.

 // In order to compile this code, follow these steps:
 //  - Add the path "%HEDS_2_ANSIC%/include" to your compiler's include paths.
 //  - Make sure you add "%HEDS_2_ANSIC%/winXX/lib/holoeye_slmdisplaysdk.lib" to your linker options.
 //  - Replace "winXX" with either "win32" or "win64", depending on your set up.

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <iostream>
#include <holoeye_slmdisplaysdk.hpp>
#include <holoeye_slmdisplaysdk_cpp.cpp>

using namespace holoeye;


int main(int argc, char* argv[])
{
    HOLOEYE_UNUSED(argc);
    HOLOEYE_UNUSED(argv);

    // Check if the installed SDK supports the required API version
    if (!heds_requires_version(2, false))
        return 1;

    // Detect SLMs and open a window on the selected SLM:
    heds_instance slm;
    heds_errorcode error = slm.open();

    if (error != heds_errorcodes::HEDSERR_NoError)
    {
        std::cerr << "ERROR: " << heds_error_string_ascii(error) << std::endl;

        return error;
    }

    // Open the SLM preview window (might have an impact on performance):
    heds_utils_slmpreview_show(true);

    // Configure the lens properties:
    const int innerRadius = heds_slm_height_px() / 3;
    const int centerX = 0;
    const int centerY = 0;

    // Calculate the phase values of a lens in a pixel-wise matrix:

    // pre-calc. helper variables:
    const float phaseModulation = 2.0f * HOLOEYE_PIF;
    const int dataWidth = heds_slm_width_px();
    const int dataHeight = heds_slm_height_px();
    auto phaseData = field<float>::create(dataWidth, dataHeight);

    std::cout << "dataWidth  = " << dataWidth << std::endl;
    std::cout << "dataHeight = " << dataHeight << std::endl;

    float innerRadius2 = (float)(innerRadius * innerRadius);

    for (int y = 0; y < dataHeight; ++y)
    {
        float* row = phaseData->row(y);

        int val_y = y - dataHeight / 2 + centerY;

        for (int x = 0; x < dataWidth; ++x)
        {
            int val_x = x - dataWidth / 2 - centerX;

            int r2 = val_x * val_x + val_y * val_y;

            row[x] = phaseModulation * (float)r2 / innerRadius2;
        }
    }

    // Show phase data on SLM:
    error = heds_show_phasevalues(phaseData, HEDSSHF_PresentAutomatic, phaseModulation);

    if (error != HEDSERR_NoError)
    {
        std::cerr << "ERROR: " << heds_error_string_ascii(error) << std::endl;

        return error;
    }

    // You may insert further code here.
    slm.close();
    // Wait until the SLM process was closed
    error = heds_utils_wait_until_closed();

    if (error != HEDSERR_NoError)
    {
        std::cerr << "ERROR: " << heds_error_string_ascii(error) << std::endl;

        return error;
    }

    std::cout << "No errors until the end";

    return 0;
}