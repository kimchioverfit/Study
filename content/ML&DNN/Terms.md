# Terms

### Flatten

Projection 과 완전히 다른 개념이니 혼동 주의

다차원 벡터를 1D array 형태로 바꾸는거임. 

Fully connected layer에 넣기 위해서 1D로 바꾸는건데, 

이후 사용하기 위해서는 정보가 추가로 필요함 (예를들어, 2D image를 1D array로 바꾸게되면 가로세로 정보없으면 알 수 없으니)

Flatten을 주로 하는 이유는, 예전 ML 에서 연산이 무거운 경우 cache localty 때문에 flatten 이용해서 연산을 빠르게 했었다.

요새는 GPU 가 2D Conv layer 같은걸로 처리해버리기 때문에, FC layer를 넣을때를 제외하고는 안쓰인다.

(물론 CNN 마지막 단계에서 요약된 feature map을 펼쳐서 Classification head 같은거에 넣는건 다른 얘기.)