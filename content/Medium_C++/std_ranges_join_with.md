# std::ranges::join_with

C++ 23 에서 추가된거 

`Flatten` 을 수행하는 std::ranges::join 의 업그레이드 버젼인데, 

(Flateen 이란, 예를들어 vector에 1,2,3 이 들어있으면 한줄로 123 만드는거)

join 과 다르게, std::ranges::join_with(",")해주면 ","를 구분자로 넣어줌.

그러면 1,2,3 이런식으로 됨. 
