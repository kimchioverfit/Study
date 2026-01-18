# 구조체 최적화 

C 구조체는 정렬 규칙에 따라 메모리 낭비 방지 가능

```cpp
struct A {
    char c;    // 1 byte
    int i;     // 4 bytes
};
```

위의 경우 A의 크기는 8바이트임. 3바이트의 패딩이 생김.

```cpp
#pragma pack(1)
struct A_packed {
    char c;
    int i;
};
#pragma pack()

```

pragra pack() 해주면 패딩없이 구조체를 만든다.

| `#pragma pack(n)` | 의미                                         |
| ----------------- | ------------------------------------------ |
| `#pragma pack(1)` | **1바이트 단위 정렬** → 가장 촘촘하게 packed (패딩 거의 없음) |
| `#pragma pack(2)` | 2바이트 단위 정렬                                 |
| `#pragma pack(4)` | 4바이트 단위 정렬 (일반적인 32비트 시스템에서 default)       |
| `#pragma pack(8)` | 8바이트 단위 정렬 (64비트 시스템에서 default일 수 있음)      |

### ⚠️ 주의사항
✅ 장점
메모리 절약 (특히 네트워크 패킷, 플래시 저장용 구조체에 유리)

바이너리 파일 포맷 매칭에 사용

❌ 단점
CPU alignment requirement 위반 → 성능 저하, 심하면 버스 오류 발생

어떤 CPU (예: ARM Cortex-A 계열)는 misaligned access에 대해 fault를 낼 수도 있음

구조체 멤버 접근이 느려질 수 있음 (메모리 bus 4/8바이트 단위로 처리되기 때문)

