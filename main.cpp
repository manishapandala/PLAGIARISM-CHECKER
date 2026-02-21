#include "MaxHeap.h"
#include <cctype>
#include <iomanip>
#include <iostream>

using namespace std;

void printMenu();
void heapSort(MaxHeap* oneMaxHeap);

int main()
{
    char input1 = 'Z';
    int vin, newVIN;
    string model, make;
    double price;
    int capacity, index = -1;
    bool success = false;

    Car oneCar;

    MaxHeap* heap1 = nullptr;
    printMenu();

    do
    {
        cout << "\nWhat action would you like to perform?" << endl;
        cin.get(input1);
        input1 = static_cast<char>(toupper(static_cast<unsigned char>(input1)));
        cin.ignore(20, '\n');

        switch (input1)
        {
            case 'C':
                cout << "\nPlease enter the heap capacity: ";
                cin >> capacity;
                cin.ignore(20, '\n');

                delete heap1;
                heap1 = new MaxHeap(capacity);
                break;

            case 'D':
                cout << "\nDelete the heap" << endl;
                delete heap1;
                heap1 = nullptr;

                heap1 = new MaxHeap(5);
                break;

            case 'E':
                if (heap1 == nullptr || heap1->getSize() == 0)
                {
                    cout << "\nEmpty heap, can NOT extract max" << endl;
                }
                else
                {
                    cout << "Before extract heap max operation:" << endl;
                    heap1->printHeap();

                    heap1->extractHeapMax();

                    cout << "After extract heap max operation:" << endl;
                    heap1->printHeap();
                }
                break;

            case 'F':
                cout << "\nEnter the car VIN you want to search: ";
                cin >> vin;
                cin.ignore(20, '\n');

                if (heap1 == nullptr)
                {
                    cout << "\nCar with VIN: " << vin << " is NOT found" << endl;
                }
                else
                {
                    index = heap1->isFound(vin);

                    if (index == -1)
                    {
                        cout << "\nCar with VIN: " << vin << " is NOT found" << endl;
                    }
                    else
                    {
                        cout << "\nCar with VIN: " << vin << " is found" << endl;
                    }
                }
                break;

            case 'I':
                cout << "\nEnter the car model: ";
                cin >> model;

                cout << "\nEnter the car make: ";
                cin >> make;

                cout << "\nEnter the car VIN: ";
                cin >> vin;
                cout << "\nEnter the car price: ";
                cin >> price;
                cin.ignore(20, '\n');

                if (heap1 == nullptr)
                {
                    cout << "\nCar \"" << model << " " << make << "\" is NOT added" << endl;
                }
                else
                {
                    success = heap1->heapInsert(vin, model, make, price);

                    if (success)
                    {
                        cout << "\nCar \"" << model << " " << make << "\" is added" << endl;
                    }
                    else
                    {
                        cout << "\nCar \"" << model << " " << make << "\" is NOT added" << endl;
                    }
                }
                break;

            case 'K':
                cout << "\nEnter the old car VIN you want to increase: ";
                cin >> vin;
                cout << "\nEnter the new car VIN: ";
                cin >> newVIN;
                cin.ignore(20, '\n');

                if (heap1 == nullptr)
                {
                    cout << "\nThe old VIN you try to increase does not exist" << endl;
                }
                else
                {
                    index = heap1->isFound(vin);

                    if (index == -1)
                    {
                        cout << "\nThe old VIN you try to increase does not exist" << endl;
                    }
                    else
                    {
                        oneCar = heap1->getCarArr()[index];
                        oneCar.vin = newVIN;
                        heap1->heapIncreaseVIN(index, oneCar);
                    }
                }
                break;

            case 'M':
                if (heap1 == nullptr || heap1->getSize() == 0)
                {
                    cout << "\nEmpty heap, can NOT get max node" << endl;
                }
                else
                {
                    Car maxCar = heap1->getHeapMax();

                    cout << "\nThe maximum heap node is:" << endl;
                    cout << left
                         << setw(8) << maxCar.vin
                         << setw(12) << maxCar.model
                         << setw(12) << maxCar.make
                         << setw(8) << fixed << setprecision(2) << maxCar.price << endl;
                }
                break;

            case 'P':
                if (heap1 == nullptr || heap1->getSize() == 0)
                {
                    cout << "\nEmpty heap, no elements" << endl;
                }
                else
                {
                    heap1->printHeap();
                }
                break;

            case 'S':
                cout << "\nHeap sort. Cars will be sorted in increasing order of their VINs" << endl;

                if (heap1 == nullptr || heap1->getSize() == 0)
                {
                    cout << "\nEmpty heap, no elements" << endl;
                }
                else
                {
                    heapSort(heap1);
                }
                break;

            case 'Q':
                delete heap1;
                heap1 = nullptr;
                break;

            case '?':
                printMenu();
                break;

            default:
                cout << "Unknown action\n";
                break;
        }
    } while (input1 != 'Q');

    return 0;
}

void heapSort(MaxHeap* oneMaxHeap)
{
    int n = oneMaxHeap->getSize();
    Car* sorted = new Car[n];

    for (int i = n - 1; i >= 0; i--)
    {
        sorted[i] = oneMaxHeap->getHeapMax();
        oneMaxHeap->extractHeapMax();
    }

    for (int i = 0; i < n; i++)
    {
        cout << left << setw(8) << sorted[i].vin
             << setw(12) << sorted[i].model
             << setw(12) << sorted[i].make
             << setw(8) << fixed << setprecision(2)
             << sorted[i].price << endl;
    }

    delete[] sorted;
}

void printMenu()
{
    cout << "Choice\t\tAction\n";
    cout << "------\t\t------\n";
    cout << "C\t\tCreate a heap\n";
    cout << "D\t\tDelete the heap\n";
    cout << "E\t\tExtract max node\n";
    cout << "F\t\tFind a Car by VIN\n";
    cout << "I\t\tInsert a Car\n";
    cout << "K\t\tIncrease the VIN\n";
    cout << "M\t\tGet the max node\n";
    cout << "P\t\tPrint the heap\n";
    cout << "S\t\tHeap Sort\n";
    cout << "Q\t\tQuit\n";
    cout << "?\t\tDisplay Help\n\n";
}
