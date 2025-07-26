# Linux Memory

## ✅ 임베디드 리눅스 메모리 모델 핵심 요약

### 1. 리눅스 메모리의 큰 구성
User space (사용자 공간)
유저 애플리케이션이 실행되는 공간. 일반적으로 0x00000000 ~ 0xBFFFFFFF (32bit 기준).

Kernel space (커널 공간)
커널이 사용하는 공간. 메모리 보호를 위해 user space와 분리되어 있음. (ex: 0xC0000000 ~ 0xFFFFFFFF)

### 2. 임베디드 시스템에서의 주요 메모리 구역

| 메모리 영역    | 설명                |
| --------- | ----------------- |
| `.text`   | 실행 코드             |
| `.data`   | 초기화된 전역/정적 변수     |
| `.bss`    | 초기화되지 않은 전역/정적 변수 |
| `heap`    | 동적 메모리 (malloc 등) |
| `stack`   | 함수 호출, 지역 변수      |
| `mmap 영역` | 공유 라이브러리, 파일 매핑 등 |


→ top, free, /proc/[pid]/maps, /proc/meminfo로 확인 가능

### 3. 임베디드에서 자주 보는 메모리 상태 지표
| 항목                        | 의미                         |
| ------------------------- | -------------------------- |
| `RSS (Resident Set Size)` | 실제 메모리에 올라간 크기             |
| `VSZ (Virtual Size)`      | 전체 가상 메모리 사용량              |
| `shared`, `heap`, `stack` | 각각 공유 메모리, 동적 할당, 호출 스택 크기 |


→ ps, pmap, smem, cat /proc/[pid]/status 등으로 분석

### 4. 커널 메모리 관련 요소

Slab Allocator (SLUB, SLOB)
커널 내부의 효율적인 메모리 할당기
→ /proc/slabinfo, slabtop 으로 확인

Page Frame / Buddy System
리눅스는 4KB 단위의 페이지로 메모리 관리
Buddy System으로 page frame을 병합/분할

kmalloc, vmalloc 차이

kmalloc: 연속된 물리 메모리 (빠름)

vmalloc: 연속된 가상 메모리 (큰 메모리 할당 시 사용)



### 5. 메모리 압축 및 스와핑

zram: 임베디드에서 압축된 swap 공간을 램에 마련

swap: 플래시 기반 스왑은 수명 문제로 일반적으로 비활성화

### 6. 메모리 관련 디버깅 도구

| 도구               | 기능               |
| ---------------- | ---------------- |
| `free` / `top`   | 전체 시스템 메모리 확인    |
| `pmap`, `smem`   | 프로세스별 상세 메모리 정보  |
| `valgrind`       | 메모리 누수, 접근 오류 검사 |
| `massif`         | 힙 메모리 프로파일링      |
| `perf`, `ftrace` | 커널 메모리 관련 성능 분석  |
