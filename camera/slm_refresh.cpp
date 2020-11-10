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

//Predefined macros required, I define them explicitly here as my compiler has not
/*#define _MSC_VER 1900
#define _WIN32 1
#define _MT 1*/
#include <math.h>
#include <iostream>
#include <fstream>
//#include <stdint.h>
//#include <crtdefs.h>
// Include files to use the pylon API.
#include <pylon/PylonIncludes.h>
#ifdef PYLON_WIN_BUILD
#    include <pylon/PylonGUI.h>
#endif

// Namespace for using pylon objects.
using namespace Pylon;

const int camheight = 256;
const int camwidth = 256;

// Namespace for using cout.
using namespace std;

// Number of images to be grabbed.
static const uint32_t c_countOfImagesToGrab = 700;

float cost_intensity(int target[camheight*camwidth], int camera[camheight*camwidth]) {
    float cost = 0;
    for (int i = 0; i < camheight*camwidth; i++) {
        cost = cost + pow(target[i] - camera[i], 2);
    }
    return cost/camheight/camwidth;
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
        CInstantCamera camera(CTlFactory::GetInstance().CreateFirstDevice());

        // Print the model name of the camera.
        cout << "Using device " << camera.GetDeviceInfo().GetModelName() << endl;

        // The parameter MaxNumBuffer can be used to control the count of buffers
        // allocated for grabbing. The default value of this parameter is 10.
        camera.MaxNumBuffer = 800;
        uint8_t* imgpointer[c_countOfImagesToGrab];
        uint8_t* targetpointer;
        int counter = 0;
        // Start the grabbing of c_countOfImagesToGrab images.
        // The camera device is parameterized with a default configuration which
        // sets up free-running continuous acquisition.

        camera.StartGrabbing(1);

        // This smart pointer will receive the grab result data.
        CGrabResultPtr ptrGrabResult_target;

        // Camera.StopGrabbing() is called automatically by the RetrieveResult() method
        // when c_countOfImagesToGrab images have been retrieved.
        while (camera.IsGrabbing())
        {
            // Wait for an image and then retrieve it. A timeout of 5000 ms is used.
            camera.RetrieveResult(5000, ptrGrabResult_target, TimeoutHandling_ThrowException);

            // Image grabbed successfully?
            if (ptrGrabResult_target->GrabSucceeded())
            {
                // Access the image data.
                //cout << "SizeX: " << ptrGrabResult->GetWidth() << endl;
                //cout << "SizeY: " << ptrGrabResult->GetHeight() << endl;
                const uint8_t* pImageBuffer_target = (uint8_t*)ptrGrabResult_target->GetBuffer();
                targetpointer= (uint8_t*)pImageBuffer_target;

                //cout << "Gray value of first pixel: " << (uint32_t)pImageBuffer[0] << endl << endl;

#ifdef PYLON_WIN_BUILD
                // Display the grabbed image.
                Pylon::DisplayImage(1, ptrGrabResult);
#endif
            }
            else
            {
                cout << "Error: " << ptrGrabResult->GetErrorCode() << " " << ptrGrabResult->GetErrorDescription() << endl;
            }

            counter++;
        }

        counter--;
        camera.StartGrabbing(c_countOfImagesToGrab);

        // This smart pointer will receive the grab result data.
        CGrabResultPtr ptrGrabResult;

        // Camera.StopGrabbing() is called automatically by the RetrieveResult() method
        // when c_countOfImagesToGrab images have been retrieved.
        while (camera.IsGrabbing())
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
                imgpointer[counter] = (uint8_t*)pImageBuffer;

                //cout << "Gray value of first pixel: " << (uint32_t)pImageBuffer[0] << endl << endl;

#ifdef PYLON_WIN_BUILD
                // Display the grabbed image.
                Pylon::DisplayImage(1, ptrGrabResult);
#endif
            }
            else
            {
                cout << "Error: " << ptrGrabResult->GetErrorCode() << " " << ptrGrabResult->GetErrorDescription() << endl;
            }

            counter++;
        }

        int cost[c_countOfImagesToGrab];
        int img[c_countOfImagesToGrab][camheight * camwidth];
        int target[camheight * camwidth];

        for (int j = 0; j < camheight*camwidth; j++)
        {
            target[j] = *(targetpointer + j);
        }

        for (int i = 0; i < c_countOfImagesToGrab; i++)
        {
            
            for (int j = 0; j < camheight * camwidth; j++)
            {
                img[i][j] = *(imgpointer[i] + j);
                
            }
            cost[i] = cost_intensity(target, img[i]);
        }

        // open a file in write mode.
        ofstream outfile;
        outfile.open("slm_refresh.csv");

        for (int i = 0; i < c_countOfImagesToGrab; i++) 
        {
            outfile << cost[i] << ",";
            
        }

        outfile.close();
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

