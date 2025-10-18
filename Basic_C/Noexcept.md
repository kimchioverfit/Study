# noexcept

말그대로 except 를 던지지 않게 하는 것.

어떻게 활용하지?

-> 최적화를 노릴때 응용할 수 있다.

예를들어, 아래와 같은 구조체가 있다고 하자.

```cpp
struct{
    A(){};
    A(const A&){};
    A(A&&) noexcept{};
}

int main(){
    std::vector<A> v;
    v.push_back(A{});
}
```

위 코드를 실행하면, 

우선 vector는 내부적으로 move가 가능한지 체크한다. (noexcept가 있는지 확인함)

noexcept가 있다면 move를 수행하고, 없으면 copy를 수행하는데, 이는 성능에 영향을 미칠 수 있다.
