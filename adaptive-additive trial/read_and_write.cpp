// Playing_around.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <fstream>

using namespace std;

int main()
{
      
    // Snippet of code to write to a file 

    int data[10][10];
    // open a file in write mode.
    ofstream outfile;
    outfile.open("afile.dat");

    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 10; j++) {
            data[i][j] = i + j;

            // write inputted data into the file.
            outfile << data[i][j] << " ";
        }
        outfile << endl;
    }
    
    outfile.close();

    // Snippet of code to read from a file
    int data1[10][10];

    ifstream infile;
    infile.open("afile.dat");

    for (int m = 0; m < 10; m++) {
        for (int n = 0; n < 10; n++) {
            infile >> data1[m][n];
            cout << data1[m][n] << " ";
        }
        cout << endl;
    }

    infile.close();

    for (int p = 0; p < 10; p++) {
        for (int q = 0; q < 10; q++) {
            if (data[p][q] != data1[p][q]) {
                cout << "Matrices aren't equal" << endl;
            }
            else {
                cout << "Arrays are equal" << endl;
            }
        }

    }

    return 0;
}
