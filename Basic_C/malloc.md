# malloc 동적 할당 

C에서 동적인 메모리 할당을 할 때 기본적인 형태 

1. malloc의 역할
Heap 영역에서 지정한 크기만큼 메모리를 할당하고
그 첫 번째 바이트의 주소를 반환.

반환 타입은 void* (아무 타입도 아닌 포인터)이므로, 원하는 타입으로 형변환해야.

```cpp
#include <stdlib.h>

int *p = (int *)malloc(sizeof(int)); // int 1개 크기만큼 heap에 메모리 할당
// 참고로 C에는 암묵적인 캐스팅이 있으므로 (int *)이걸 안해주는게 사실 더 좋다.
int * p = malloc(sizeof(int));
```

```cpp
int *arr = (int *)malloc(sizeof(int) * 5); // int 5개짜리 배열
for (int i = 0; i < 5; i++) {
    arr[i] = i + 1; // arr[i] == *(arr + i)
}
free(arr);

```

### 주의 사항

malloc으로 할당한 메모리는 free()로 직접 해제해야 함.

해제 안 하면 메모리 누수(memory leak) 발생.

해제 후 해당 포인터를 다시 사용하면 **dangling pointer** 문제 발생 → 보통 p = NULL;로 초기화.