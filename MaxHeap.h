#ifndef MAXHEAP_H
#define MAXHEAP_H

#include <iomanip>
#include <iostream>
#include <string>

struct Car
{
    std::string model;
    std::string make;
    int vin;
    double price;
};

class MaxHeap
{
private:
    Car* carArr;
    int capacity;
    int size;

    static void swapCars(Car& first, Car& second)
    {
        Car temp = first;
        first = second;
        second = temp;
    }

public:
    explicit MaxHeap(int cap)
    {
        if (cap <= 0)
        {
            cap = 1;
        }

        capacity = cap;
        size = 0;
        carArr = new Car[capacity];
    }

    ~MaxHeap()
    {
        delete[] carArr;
        std::cout << "\nThe number of deleted cars is: " << size << std::endl;
    }

    Car* getCarArr()
    {
        return carArr;
    }

    int getSize() const
    {
        return size;
    }

    int getCapacity() const
    {
        return capacity;
    }

    int leftChild(int parentIndex) const
    {
        return (2 * parentIndex) + 1;
    }

    int rightChild(int parentIndex) const
    {
        return (2 * parentIndex) + 2;
    }

    int parent(int childIndex) const
    {
        return (childIndex - 1) / 2;
    }

    int isFound(int aVin) const
    {
        for (int i = 0; i < size; ++i)
        {
            if (carArr[i].vin == aVin)
            {
                return i;
            }
        }
        return -1;
    }

    void heapify(int index)
    {
        int largest = index;
        int left = leftChild(index);
        int right = rightChild(index);

        if (left < size && carArr[left].vin > carArr[largest].vin)
        {
            largest = left;
        }

        if (right < size && carArr[right].vin > carArr[largest].vin)
        {
            largest = right;
        }

        if (largest != index)
        {
            swapCars(carArr[index], carArr[largest]);
            heapify(largest);
        }
    }

    bool heapInsert(int vin, const std::string& model, const std::string& make, double price)
    {
        if (isFound(vin) != -1)
        {
            std::cout << "\nDuplicated Car. Not added" << std::endl;
            return false;
        }

        if (size == capacity)
        {
            int newCapacity = capacity * 2;
            if (newCapacity <= 0)
            {
                newCapacity = 1;
            }

            Car* expandedArr = new Car[newCapacity];
            for (int i = 0; i < size; ++i)
            {
                expandedArr[i] = carArr[i];
            }

            delete[] carArr;
            carArr = expandedArr;
            capacity = newCapacity;

            std::cout << "\nReach the capacity limit, double the capacity now.\n"
                      << "\nThe new capacity now is " << capacity << std::endl;
        }

        Car newCar;
        newCar.vin = vin;
        newCar.model = model;
        newCar.make = make;
        newCar.price = price;

        carArr[size] = newCar;
        int index = size;
        ++size;

        while (index > 0 && carArr[index].vin > carArr[parent(index)].vin)
        {
            swapCars(carArr[index], carArr[parent(index)]);
            index = parent(index);
        }

        return true;
    }

    bool heapIncreaseVIN(int index, Car oneCarWithNewVIN)
    {
        if (index < 0 || index >= size)
        {
            std::cout << "\nThe old VIN you try to increase does not exist" << std::endl;
            return false;
        }

        int oldVIN = carArr[index].vin;
        int newVIN = oneCarWithNewVIN.vin;

        if (newVIN <= oldVIN)
        {
            std::cout << "\nIncrease VIN error: new VIN is smaller than current VIN" << std::endl;
            return false;
        }

        if (isFound(newVIN) != -1)
        {
            std::cout << "\nThe new VIN you entered already exist, increase VIN operation failed" << std::endl;
            return false;
        }

        std::cout << "\nBefore increase VIN operation:" << std::endl;
        printHeap();

        carArr[index] = oneCarWithNewVIN;
        while (index > 0 && carArr[index].vin > carArr[parent(index)].vin)
        {
            swapCars(carArr[index], carArr[parent(index)]);
            index = parent(index);
        }

        std::cout << "\nCar with old VIN: " << oldVIN << " is increased to new VIN: " << newVIN << std::endl;
        std::cout << "\nAfter increase VIN operation: " << std::endl;
        printHeap();
        return true;
    }

    Car getHeapMax() const
    {
        if (size == 0)
        {
            return Car{"", "", -1, 0.0};
        }

        return carArr[0];
    }

    void extractHeapMax()
    {
        if (size == 0)
        {
            return;
        }

        carArr[0] = carArr[size - 1];
        --size;
        if (size > 0)
        {
            heapify(0);
        }
    }

    void printHeap() const
    {
        if (size == 0)
        {
            std::cout << "\nEmpty heap, no elements" << std::endl;
            return;
        }

        std::cout << "\nHeap capacity = " << capacity << std::endl;
        std::cout << "\nHeap size = " << size << "\n" << std::endl;

        for (int i = 0; i < size; ++i)
        {
            std::cout << std::left
                      << std::setw(8) << carArr[i].vin
                      << std::setw(12) << carArr[i].model
                      << std::setw(12) << carArr[i].make
                      << std::setw(8) << std::fixed << std::setprecision(2) << carArr[i].price << std::endl;
        }
    }
};

#endif
