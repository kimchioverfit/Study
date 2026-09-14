// g++ -std=c++11 -pthread Multi_Thread_Linux_CPP_Standard.cpp -o Multi_Thread_Linux_CPP_Standard
// ./Multi_Thread_Linux_CPP_Standard


// Multi_Thread_Linux_CPP_Standard.cpp
#include <iostream>
#include <thread>

void say_hello(int id) {
    std::cout << "Hello from std::thread " << id << std::endl;
}

int main() {
    std::thread t1(say_hello, 1);
    std::thread t2(say_hello, 2);

    t1.join();
    t2.join();

    return 0;
}
