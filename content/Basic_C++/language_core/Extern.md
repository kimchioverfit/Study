# extern "C"

extern에 대해 시작하기에 앞서, 

우선 cpp에 대해서 복습해보자.

cpp는 overload, override 를 지원한다.

parameter type이나 수가 다른 경우 static polymophysm (Overload)이다.

return type 이 달라질 수 있는것이 dynamic polymophysm (Override)이다.

(물론 둘 다 함수 내용은 다르게 가능)

여기서, Overload 가 문제된다. 

우선, Override의 경우 c++에서 symbol로 저장될 때 

```
_ZN4Base3fooEv        ; Base::foo()
_ZN7Derived3fooEv     ; Derived::foo()
``` 
이런형태로 저장되지만, 

Overload의 경우

```
_Z3fooi(foo(int))
_Zefood(foo(double))
```

이런 식으로, 저장되게 된다. 

여기까지는 정상적인 동작이지만, C에서 이를 활용해야 하는 경우 문제가 발생한다.

C에서는 namespace 라는 개념이 없으므로, 

foo를 호출하고 싶어서 foo()를 불렀음에도 심볼에는 없기 때문에 Link 에러가 발생한다.

그래서, C++에서 내보낼 때 망글링을 못하게 막아야한다.

```cpp
// cpp 내부
static int foo_int(int x)    { return x + 1; }
static double foo_double(double x) { return x + 0.5; }

extern "C" int    foo_i(int x)    { return foo_int(x); }     // "foo_i"
extern "C" double foo_d(double x) { return foo_double(x); }  // "foo_d"
```
위와 같이 extern "C" 를 이용해주면, mangling 을 금지하고, foo_i, foo_d 형태의 이름으로 만들어서 내보낸다.