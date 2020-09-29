// Camera_trial.cpp : This file contains the 'main' function. Program execution begins and ends there.

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

// Include files to use the pylon API.
#include <pylon/PylonIncludes.h>
#include <pylon/BaslerUniversalInstantCamera.h>
#ifdef PYLON_WIN_BUILD
#    include <pylon/PylonGUI.h>
#endif

#define A 0.8
#define CAMHEIGHT 1088
#define CAMWIDTH 2048

using namespace Basler_UniversalCameraParams;

// Namespace for using pylon objects.
using namespace Pylon;
// Namespace for using cout.
using namespace std;

// Number of images to be grabbed.
static const uint32_t c_countOfImagesToGrab = 160;

float cost_intensity(int target[CAMHEIGHT][CAMWIDTH], int camera[CAMHEIGHT][CAMWIDTH]){
    float cost = 0;
    for(int i=0; i<CAMHEIGHT; i++)
      for(int j=0; j<CAMWIDTH; j++)
        cost = cost + (target[i][j]-camera[i][j])*(target[i][j]-camera[i][j]);
    return cost/CAMHEIGHT/CAMWIDTH;
}

void set_target(uint8_t target[CAMHEIGHT][CAMWIDTH]){
    for(int i=0; i<CAMHEIGHT; i++)
      for(int j=0; j<CAMWIDTH; j++){
        if((i == CAMHEIGHT/2) && (j==CAMWIDTH/2))
          target[i][j] = 1;
        else
          target[i][j] = 0;
      }
}

int main(int argc, char* argv[])
{
    // The exit code of the sample application.
    int exitCode = 0;
    uint8_t target_intensity[CAMHEIGHT][CAMWIDTH] = 0;
    set_target(target_intensity);
    // Before using any pylon methods, the pylon runtime must be initialized. 
    PylonInitialize();
    try
    {
        // Create an instant camera object with the camera device found first.
        // CInstantCamera camera(CTlFactory::GetInstance().CreateFirstDevice());
        CBaslerUniversalInstantCamera camera(CTlFactory::GetInstance().CreateFirstDevice());
        // Print the model name of the camera.
        cout << "Using device " << camera.GetDeviceInfo().GetModelName() << endl;
        cout << "Device initialized" << endl;
        // The parameter MaxNumBuffer can be used to control the count of buffers
        // allocated for grabbing. The default value of this parameter is 10.
        camera.MaxNumBuffer = 200;
        //trial code begins here
        /*INodeMap& nodemap = camera.GetNodeMap();
        // Set the upper limit of the camera's frame rate to 30 fps
        CBooleanParameter(nodemap, "AcquisitionFrameRateEnable").SetValue(true);
        CFloatParameter(nodemap, "AcquisitionFrameRate").SetValue(30.0); */
        camera.Open();
        camera.DeviceLinkThroughputLimitMode.SetValue("Off");

        //camera.GetNodeMap();
        camera.AcquisitionFrameRateEnable.SetValue(true);
        camera.AcquisitionFrameRate.SetValue(170.0);
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

        if (error != HEDSERR_NoError)
        {
            std::cerr << "ERROR: " << heds_error_string_ascii(error) << std::endl;
            return error;
        }

        // Start the grabbing of c_countOfImagesToGrab images.
        // The camera device is parameterized with a default configuration which
        // sets up free-running continuous acquisition.
        camera.StartGrabbing(c_countOfImagesToGrab);
        CBaslerUniversalGrabResultPtr ptrGrabResult;
        // This smart pointer will receive the grab result data.
        // CGrabResultPtr ptrGrabResult;
        // Camera.StopGrabbing() is called automatically by the RetrieveResult() method
        // when c_countOfImagesToGrab images have been retrieved.
        float cost = 99999999;
        float threshold = 1;
        while (camera.IsGrabbing() && (cost > threshold))
        {
            // Wait for an image and then retrieve it. A timeout of 5000 ms is used.
            camera.RetrieveResult(5000, ptrGrabResult, TimeoutHandling_ThrowException);

            // Image grabbed successfully?
            if (ptrGrabResult->GrabSucceeded())
            {
                // Access the image data.
                const uint8_t* pImageBuffer = (uint8_t*)ptrGrabResult->GetBuffer();
                cost = cost_intensity(target_intensity, pImageBuffer);
                cout << ptrGrabResult->GetImageSize() << endl;

                float img_fb[CAMHEIGHT][CAMWIDTH];
                for(int i=0; i<CAMHEIGHT; i++)
                  for(int j=0; j<CAMWIDTH; j++){
                    img_fb[i][j] = A*sqrt(double((*(*(image_fb+i)+j)))) + (1-A)*sqrt(double(target_intensity[i][j]))
                  }
                ////IFFT
                ////GET THE FFTW3 LIBRARY
                float img_ifft_phase[CAMHEIGHT][CAMWIDTH];
                //USE the library

                int del_y = (CAMHEIGHT-dataHeight)/2;
                int del_x = (CAMWIDTH - dataWidth)/2;

                ////SLM display matrix data.
                for (int y = 0; y < dataHeight; ++y)
                {
                    float* row = phaseData->row(y);
                    for (int x = 0; x < dataWidth; ++x)
                    {
                        row[x] = phaseModulation * img_ifft_phase[del_y+y][del_x+x];
                    }
                }
                // Show phase data on SLM:
                error = heds_show_phasevalues(phaseData, HEDSSHF_PresentAutomatic, phaseModulation);


#ifdef PYLON_WIN_BUILD
                // Display the grabbed image.
                Pylon::DisplayImage(1, ptrGrabResult);
#endif
            }
            else
            {
                cout << "Error: " << ptrGrabResult->GetErrorCode() << " " << ptrGrabResult->GetErrorDescription() << endl;
            }
        }

        // You may insert further code here.
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
        cerr << "An exception occurred." << endl << e.GetDescription() << endl;
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
