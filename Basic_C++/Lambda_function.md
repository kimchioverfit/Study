# Lambda function

짧은 람다함수는 컴파일러가 inline화 시켜줌

지역성을 높여서 cache 효율성도 올려줌

사용방법 

[capture](parameter){defenition};

여기서, capture 의 존재 이유는, 외부의 변수를 함수 내에서 이용할 때 필요한 것.

의문 : 그냥 Parameter를 여러개 받게 만들면 되는 것 아닌가?
답변 : 어떤 함수들은 parameter로 함수를 받을 수 있는데, (STL, Callback, 비동기 framework 등) 그때 인자로 람다함수를 넣을 수 있다.
문제는 인자로 사용되는 함수를 단항 함수로만 받을 수 있는 함수들이 있는데 (std::remove_if 등) 이런 함수에 파라미터로 넣으려면 어쩔 수 없음.

```cpp
auto add = [](int a, int b) { return a + b; };
```

```cpp
std::vector<int> v = {3, 1, 4};
std::sort(v.begin(), v.end(), [](int a, int b){ return a > b; });  
```

```cpp
int result = [](int a, int b) { return a + b; }(3, 5);  // 이렇게 마지막에 (); 해주면 선언하자마자 실행
std::cout << result << "\n";  // 출력: 8
```