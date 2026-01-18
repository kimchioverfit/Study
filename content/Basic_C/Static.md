# Static

Static은 활용 방법이 여러가지라서 하나로 단정하기는 어려우나, 

보통 Scope (함수, namespace) 안에서만 이용하게끔 제한하는 용도로 쓰임.

그렇기 때문에, Static 과 void + override 를 통한 Runtime 다형성 형성이 불가능함. 
(애초에 void + override 는 vtable이용하는데, static 키워드를 이용하면 compile time에 정해지기 때문) -> inline 가능성 높음
(compile time 에 정해진다는 것은, 동시에 this를 쓰는 것도 불가능하다는 얘기임 (instance))

대신, 정적인 다형성인 overloading은 가능하다. 

참고로, compile time에 주소를 바로 박는다.