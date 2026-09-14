    // g++ -std=c++11 -pthread Multi_Thread_Linux_POSIX.cpp -o Multi_Thread_Linux_POSIX
    // ./Multi_Thread_Linux_POSIX

    // Multi_Thread_Linux_POSIX.cpp
    #include <iostream>
    #include <pthread.h>

    void* say_hello(void* arg) {
        int id = *(int*)arg;
        std::cout << "Hello from pthread " << id << std::endl;
        return nullptr;
    }

    int main() {
        pthread_t t1, t2;
        int id1 = 1, id2 = 2;

        pthread_create(&t1, nullptr, say_hello, &id1);
        pthread_create(&t2, nullptr, say_hello, &id2);

        pthread_join(t1, nullptr);
        pthread_join(t2, nullptr);

        return 0;
    }
