
# Function pointer

함수를 가리키는 포인터, 

```cpp
반환형 (*포인터이름)(매개변수 타입);
```

으로 사용함. 


### 사용 이유

1. Callback function
2. Strategy Pattern
3. Table based dispatch
4. Plugin system
5. C - style 연동 (callback function)

---

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