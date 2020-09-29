// target_intensity_capture.cpp
// This file captures the intensity profile on the screen and stores the pixel values in a file
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

// Include standard libraries for timestamps and file processing
#include <ctime>
#include <fstream>

// Include files to use the pylon API.
#include <pylon/PylonIncludes.h>

#include <pylon/BaslerUniversalInstantCamera.h>


#ifdef PYLON_WIN_BUILD
#    include <pylon/PylonGUI.h>
#endif

using namespace Basler_UniversalCameraParams;


// Namespace for using pylon objects.
using namespace Pylon;

// Namespace for using cout.
using namespace std;

// Number of images to be grabbed.
static const uint32_t c_countOfImagesToGrab = 1;

int main(int argc, char* argv[])
{
    // The exit code of the sample application.
    int exitCode = 0;
    
    // open a file in write mode.
    ofstream target_data_file;
    target_data_file.open("target_intensity.txt");

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
        
        camera.MaxNumBuffer = 2;

        cout << "Max buffers set" << endl;
     
        //trial code begins here
        
        camera.Open();
        camera.DeviceLinkThroughputLimitMode.SetValue("Off");
        
        //Set the camera Region of Interest (ROI) to maximize allowed frame rate
        int64_t maxWidth = camera.Width.GetMax();  //Maximum width of camera in pixels
        int our_width = 1920;
        int our_height = 1080;
        camera.Width.SetValue(our_width);         // Set pixel width as lower than full allowed width
        camera.Height.SetValue(our_height);       // Set pixel height as lower than full allowed height
        int our_offsetx = 64;
        int our_offsety = 4;
        camera.OffsetX.SetValue(our_offsetx);     // Setting origin of the sensor array from the top left corner
        camera.OffsetY.SetValue(our_offsety);
        cout << "Working with an image frame size of: " << our_width * our_height << " pixels" << endl;
        
        int data[our_height][our_width];
    
        camera.AcquisitionFrameRateEnable.SetValue(true);
        cout << "frame rate enabled" << endl;
        camera.AcquisitionFrameRate.SetValue(100.0);
        cout << "frame rate set" << endl;
        double rate = camera.ResultingFrameRate.GetValue();
        cout << "frame rate is:" << rate << endl;
       
       
        cout << "All okay till here" << endl;

       
        //trial code ends here
       
        // Start the grabbing of c_countOfImagesToGrab images.
        // The camera device is parameterized with a default configuration which
        // sets up free-running continuous acquisition.
        camera.StartGrabbing(c_countOfImagesToGrab);

        CBaslerUniversalGrabResultPtr ptrGrabResult;
        // This smart pointer will receive the grab result data.
       // CGrabResultPtr ptrGrabResult;

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
                for(int i=0; i < our_height ; i++){
                 for(int j=0; j < our_width ; j++){
                     data[i][j] = (uint32_t)pImageBuffer[i*our_width + j];
                     target_data_file << data[i][j] << " ";
                 
                 }
                    target_data_file << endl;
                }
                // write inputted data into the file.
                //target_data_file << data << endl;
                //cout << "Gray value of first pixel: " << (uint32_t)pImageBuffer[0] << endl << endl;
                //cout << ptrGrabResult->GetImageSize() << endl;
                
#ifdef PYLON_WIN_BUILD
                // Display the grabbed image.
                //Pylon::DisplayImage(1, ptrGrabResult);
#endif
            }
            else
            {
                cout << "Error: " << ptrGrabResult->GetErrorCode() << " " << ptrGrabResult->GetErrorDescription() << endl;
            }
        }
        
    
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