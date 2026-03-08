# Callback function

콜백함수란? 

콜백 함수(callback function)는 어떤 함수의 인자로 전달되어, 그 함수 내부에서 호출되는 함수. 
다시 말해, "나중에 호출될 함수"를 미리 전달해두는 것

🎯 왜 쓰나?
유연한 동작 지정
함수 동작 중 일부만 사용자에게 위임 → 사용자 정의 동작 가능

이벤트 기반 프로그래밍
사용자 입력, 네트워크 수신 등 "이벤트"에 반응

라이브러리/프레임워크 확장성
내부 로직은 숨기고, 외부에서 특정 동작만 바꿀 수 있도록 함


```cpp
bool compare(int a, int b) { return a > b; }
std::sort(arr, arr + n, compare);  // compare는 함수 포인터
```
위 케이스를 보면 알 수 있듯이, 함수를 파라미터로 쓸 수 있고, 

```cpp
#include <iostream>
using namespace std;

void doMath(int x, int y, int (*operation)(int, int)) {
    cout << "결과: " << operation(x, y) << endl;
}

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

int main() {
    doMath(5, 3, add);  // 콜백으로 add 전달
    doMath(5, 3, sub);  // 콜백으로 sub 전달
    return 0;
}
```

이런 식으로 사용 가능.



**`C-style 연동`**

C 라이브러리는 객체지향 기능이 없기 때문에,
콜백(callback)을 넘길 때는 **함수 포인터**를 씀.

🧩 C에서는?
상태(state) 없이 함수만 전달할 수 있다.

void (*callback)(int) 같은 식으로 정적 함수 주소만 넘길 수 있음

객체나 캡처된 환경은 못 넘깁니다.

C는 this 포인터 같은 게 없기 때문에, 콜백 함수 내부에서 어떤 컨텍스트도 유지할 수 없음

🔍 그래서 C는 콜백을 어떻게 처리하냐?
"내가 함수 주소만 받아서,
나중에 그 함수를 직접 호출할게."

이 구조만 가능하므로:

콜백 타입은 함수 포인터

콜백은 글로벌 또는 static 함수만 사용 가능

상태를 전달하려면 void* user_data 같은 별도 데이터 포인터를 같이 전달해야 함


⚠️ C++ 연동 시 주의
비멤버 함수나 static 멤버 함수만 C-style 콜백으로 전달 가능

일반 멤버 함수는 this 포인터가 암묵적으로 필요하기 때문에 콜백으로 직접 쓸 수 없음