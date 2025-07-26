#include <iostream>
#include <unistd.h>
#include <sys/wait.h>
#include <pthread.h>
#include <cstring>
#include <mutex>
#include <vector>

std::mutex mtx;
std::vector<std::string> shared_messages;

struct ThreadArg {
    int pipe_fd;
    int id;
};

void* thread_func(void* arg) {
    ThreadArg* t_arg = (ThreadArg*)arg;
    char buffer[128];

    while (true) {
        ssize_t count = read(t_arg->pipe_fd, buffer, sizeof(buffer) - 1);
        if (count <= 0) break;

        buffer[count] = '\0';

        // 뮤텍스 잠금 후 공유 데이터 접근
        std::lock_guard<std::mutex> lock(mtx);
        shared_messages.push_back(buffer);
        std::cout << "[Thread " << t_arg->id << "] Received: " << buffer;
    }

    return nullptr;
}

int main() {
    int pipefd[2];
    // pipefd[0] 는 읽기 전용 디스크립터
    // pipefd[1] 은 쓰기 전용 디스크럽터
    // 부모 프로세스에서 write해서 자식 프로세스에서 read 하는거임
    if (pipe(pipefd) == -1) {
        perror("pipe");
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 2;
    }
    else if (pid == 0) {
        // 자식 프로세스
        close(pipefd[1]); // write end 닫기

        pthread_t t1, t2;
        ThreadArg arg1 = { pipefd[0], 1 };
        ThreadArg arg2 = { pipefd[0], 2 };

        pthread_create(&t1, nullptr, thread_func, &arg1);
        pthread_create(&t2, nullptr, thread_func, &arg2);

        pthread_join(t1, nullptr);
        pthread_join(t2, nullptr);

        // 공유 데이터 출력 (뮤텍스 보호 하에)
        {
            std::lock_guard<std::mutex> lock(mtx);
            std::cout << "\n[Child] Summary of messages:\n";
            for (const auto& msg : shared_messages) {
                std::cout << "- " << msg;
            }
        }

        close(pipefd[0]);
        return 0;
    }
    else {
        // 부모 프로세스
        close(pipefd[0]); // read end 닫기

        const char* messages[] = {
            "Hello from parent 1\n",
            "Hello from parent 2\n",
            "IPC is working\n",
            "Thread-safe logging\n",
        };

        for (const char* msg : messages) {
            write(pipefd[1], msg, strlen(msg));
            usleep(100000); // 일부러 천천히 쓰기
        }

        close(pipefd[1]); // 쓰기 종료
        wait(nullptr);    // 자식 종료 대기
        std::cout << "\n[Parent] Child process finished\n";
    }

    return 0;
}
