# Polymorphism

다형성에는 크게 2가지가 있다.

1. Static
2. Dynamic 


### 1. Static Polymorphism

- Overloading
- Template
- CRTP 

등이 여기에 속한다. 

Runtime Overhead가 없는 형태이고, Vtable과 관계없다.
즉, Compile time에 결정된다는 이야기.

질문 : Template는 동적으로 type이 결정되는거 아닌가요?
답 : 아니다. Template function은 무조건 compile time에 type을 알 수 있을때만 쓸 수 있다.
그래서 type이 변할 수 있는 변수는 parameter로 쓸 수 없음.

### 2. Dynamic Polymorphism

- override

Runtime 에 어떤 함수를 쓸 지 결정되는 것들.
