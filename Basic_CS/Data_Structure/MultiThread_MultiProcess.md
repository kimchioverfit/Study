# Multi thread vs Multi process

### ✅ 차이 요약

| 구분          | 멀티스레드 (`threading`) | 멀티프로세스 (`multiprocessing`) |
| ----------- | ------------------- | -------------------------- |
| 적합한 작업      | I/O 바운드             | CPU 바운드                    |
| GIL 영향      | 있음 (병렬 연산 제한됨)      | 없음 (진정한 병렬 처리 가능)          |
| 메모리 공유      | 공유 (동기화 필요)         | 각 프로세스는 별도 메모리 공간 사용       |
| 속도 (작업별 차이) | 대기 많은 작업에서 효율적      | 계산량 많은 작업에서 효율적            |
| 항목     | 멀티스레드 (`threading`) | 멀티프로세스 (`multiprocessing`)      |
| 데이터 공유 | 전역 변수로 가능           | 별도 매커니즘 필요 (`Manager`, `Queue`) |
| 동기화 문제 | 발생 가능 (경합 조건 등)     | 기본적으로 없음                        |
| 장점     | 공유 자원 접근이 빠름        | 충돌 위험 없음                        |
| 단점     | 동기화 필요, GIL의 영향 있음  | 데이터 전달 시 오버헤드 있음                |

---

### ✅ 1. 멀티스레딩 예제 (I/O 바운드에 유리)

I/O 바운드 작업에 유리합니다 (예: time.sleep, 네트워크 요청 등)


```python
import threading
import time

def task(name):
    print(f"{name} 시작")
    time.sleep(2)
    print(f"{name} 종료")

start_time = time.time()

threads = []
for i in range(5):
    t = threading.Thread(target=task, args=(f"스레드-{i}",))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"총 소요 시간 (멀티스레드): {time.time() - start_time:.2f}초")

```

---

### ✅ 2. 멀티프로세싱 예제 (CPU 바운드에 유리)

CPU 바운드 작업에 유리합니다 (예: 수학 연산, 이미지 처리 등)


```python
import multiprocessing
import time

def compute(n):
    print(f"프로세스 시작 (PID: {multiprocessing.current_process().pid})")
    total = 0
    for i in range(n):
        total += i * i
    print(f"프로세스 종료 (PID: {multiprocessing.current_process().pid})")
    return total

if __name__ == '__main__':
    start_time = time.time()
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(compute, [10**6] * 4)  # 4개 작업 병렬 처리
    print(f"총 소요 시간 (멀티프로세스): {time.time() - start_time:.2f}초")

```

