/******************************************************************************

                              Online C++ Compiler.
               Code, Compile, Run and Debug C++ program online.
Write your code in this editor and press "Run" button to compile and execute it.

*******************************************************************************/

// Camera_trial.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

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

#include <iostream>
#include <cmath>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <time.h>
#include <holoeye_slmdisplaysdk.hpp>
#include <holoeye_slmdisplaysdk_cpp.cpp>
using namespace holoeye;


// Grab.cpp
/*
    Note: Before getting started, Basler recommends reading the "Programmer's Guide" topic
    in the pylon C++ API documentation delivered with pylon.
    If you are upgrading to a higher major version of pylon, Basler also
    strongly recommends reading the "Migrating from Previous Versions" topic in the pylon C++ API documentation.
    This sample illustrates how to grab and process images using the CInstantCamera class.
    The images are grabbed and processed asynchronously, i.e.,
    while the application is processing a buffer, the acquisition of the next buffer is done
    in parallel.
    The CInstantCamera class uses a pool of buffers to retrieve image data
    from the camera device. Once a buffer is filled and ready,
    the buffer can be retrieved from the camera object for processing. The buffer
    and additional image data are collected in a grab result. The grab result is
    held by a smart pointer after retrieval. The buffer is automatically reused
    when explicitly released or when the smart pointer object is destroyed.
*/

// Include files to use the pylon API.
#include <pylon/PylonIncludes.h>

#include <pylon/BaslerUniversalInstantCamera.h>


#ifdef PYLON_WIN_BUILD
#    include <pylon/PylonGUI.h>
#endif

#define _USE_MATH_DEFINES
#define A 0.5
#define THRESHOLD 1
using namespace Basler_UniversalCameraParams;


// Namespace for using pylon objects.
using namespace Pylon;

// Namespace for using cout.
using namespace std;

// Number of images to be grabbed.
static const uint32_t c_countOfImagesToGrab = 160;


// Defining cost function
float cost(uint32_t* image, uint32_t* target, int size_img){
    float q=0;
    for(int p=0; p< size_img; p++){
       q += (image[i]-target[i])*(image[i]-target[i]); 
    }
    return q/size_img;
};

// Defining flip function for Monte-Carlo method

void flip(float* DATA, int NUMBER, int D, float* temp){
    int t;
    int random[D];
    t = srand(time(NULL));
    for (int m=0; m<D; m++){
        random[m] = rand()%NUMBER;
        temp[random[m]] = (M_PI-DATA[random[m]]);
    }
}

int main(int argc, char* argv[])
{
    // The exit code of the sample application.
    int exitCode = 0;

    // Before using any pylon methods, the pylon runtime must be initialized. 
    PylonInitialize();
    try
    {
        // Create an instant camera object with the camera device found first.
      
        CBaslerUniversalInstantCamera camera(CTlFactory::GetInstance().CreateFirstDevice());
        // Print the model name of the camera.
        cout << "Using device " << camera.GetDeviceInfo().GetModelName() << endl;
        cout << "Device initialized" << endl;
        // The parameter MaxNumBuffer can be used to control the count of buffers
        // allocated for grabbing. The default value of this parameter is 10.
        camera.MaxNumBuffer = 2000;
        //trial code begins here
     
        camera.Open();
        camera.DeviceLinkThroughputLimitMode.SetValue("Off");
      
        //Set the camera Region of Interest (ROI) to maximize allowed frame rate
        int64_t maxWidth = camera.Width.GetMax();      // Maximum width of camera in pixels
        int64_t maxHeight = camera.Height.GetMax();    // Maximum height of camera in pixels
        int our_width = 1920;
        int our_height = 1080;
        camera.Width.SetValue(our_width);              // Set pixel width as lower than full allowed width
        camera.Height.SetValue(our_height);            // Set pixel height as lower than full allowed height
        int our_offsetx = 64;
        int our_offsety = 4;
        camera.OffsetX.SetValue(our_offsetx);          // Setting origin of the sensor array from the top left corner
        camera.OffsetY.SetValue(our_offsety);
        cout << "Working with an image frame size of: " << our_width * our_height << " pixels" << endl;

        //camera.GetNodeMap();
        camera.AcquisitionFrameRateEnable.SetValue(true);
        //cout << "frame rate enabled" << endl;
        camera.AcquisitionFrameRate.SetValue(150.0);
        //cout << "frame rate set" << endl;
        double rate = camera.ResultingFrameRate.GetValue();
        cout << "frame rate is:" << rate << endl;

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
        cout << "All okay till here" << endl;

        //trial code ends here
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

        int img[our_width][our_height];
        int phase_modif[our_width][our_height];
        int phase_no_modif[our_width][our_height];
        float data = row;
        for (int y = 0; y < our_height; ++y)
        {
            float* row = phaseData->row(y);
            for (int x = 0; x < our_width; ++x)
                *(phase_no_modif+y*our_width+x) = row[x];
        }
      
        float COST = 9999999999;
        float prev_cost = 9999999999;
        // Start the grabbing of c_countOfImagesToGrab images.
        // The camera device is parameterized with a default configuration which
        // sets up free-running continuous acquisition.
        camera.StartGrabbing(c_countOfImagesToGrab);
        CBaslerUniversalGrabResultPtr ptrGrabResult;
        // This smart pointer will receive the grab result data.
        // CGrabResultPtr ptrGrabResult;
        // Camera.StopGrabbing() is called automatically by the RetrieveResult() method
        // when c_countOfImagesToGrab images have been retrieved.
        while (camera.IsGrabbing() && COST > THRESHOLD)
        {
            // Wait for an image and then retrieve it. A timeout of 5000 ms is used.
            camera.RetrieveResult(5000, ptrGrabResult, TimeoutHandling_ThrowException);
            // Image grabbed successfully?
            if (ptrGrabResult->GrabSucceeded())
            {
                // Access the image data.
                //cout << "SizeX: " << ptrGrabResult->GetWidth() << endl;
                //cout << "SizeY: " << ptrGrabResult->GetHeight() << endl;
                const uint8_t* pImageBuffer = (uint8_t*)ptrGrabResult->GetBuffer();
                //cout << "Gray value of first pixel: " << (uint32_t)pImageBuffer[0] << endl;
                if (COST < prev_cost){
                    for (int x = 0; x < dataWidth; ++x){
                        for (int x = 0; x < dataWidth; ++x)
                            phase_no_modif[i] = *(phase_modif+y*our_width+i);              
                    }
                    prev_cost = COST;
                }
                //COST = cost((uint32_t)pImageBuffer, target, our_width*our_height);
                for(int M=0; M<our_width; M++){
                    for(int N=0; N<our_height; N++){
                        img[M][N] = (uint32_t)pImageBuffer[our_width*M + N];
                    }
                }
                COST = cost(img, target, our_width*our_height);
                cout << ptrGrabResult->GetImageSize() << endl;
                for (int y = 0; y < our_height; ++y)
                {
                    float* row = phaseData->row(y);
                    flip((phase_no_modif+y*our_width), our_width, cell_size, (phase_modif+y*our_width));
                    for (int x = 0; x < dataWidth; ++x)
                         row[i] = *(phase_modif+y*our_width+i);              
                }
#ifdef PYLON_WIN_BUILD
                // Display the grabbed image.
                Pylon::DisplayImage(1, ptrGrabResult);
#endif
            }
            else
            {
                cout << "Error: " << ptrGrabResult->GetErrorCode() << " " << ptrGrabResult->GetErrorDescription() << endl;
            }
            error = heds_show_phasevalues(phaseData, HEDSSHF_PresentAutomatic, phaseModulation);
        }

        // You may insert further code here.
        // Closing down system after taking keyboard input
        int spatial_end;
        cin >> spatial_end;
        slm.close();
        // Wait until the SLM process was closed
        error = heds_utils_wait_until_closed();

        if (error != HEDSERR_NoError)
        {
            std::cerr << "ERROR: " << heds_error_string_ascii(error) << std::endl;
            return error;
        }
        std::cout << "No errors until the end";
        camera.Close();
    }
    catch (const GenericException& e)
    {
        // Error handling.
        cerr << "An exception occurred." << endl
            << e.GetDescription() << endl;
        exitCode = 1;
    }
    // Comment the following two lines to disable waiting on exit.
    cerr << endl << "Press enter to exit." << endl;
    while (cin.get() != '\n');
    
    // Releases all pylon resources. 
    PylonTerminate();
    return exitCode;
}
/* Vikram's Notes:
   1) Seems like no errors are thrown up if number of images to grab equals number of buffers allocated
   2) Camera image seems to comprise 2048x1088 = 2228224 pixels of data
   3) Number of images grabbed can be a substitute for number of iterations (but no breakout condition
      will be utilized)*/
