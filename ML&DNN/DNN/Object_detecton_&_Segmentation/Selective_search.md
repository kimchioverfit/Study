# Selective search

### Main idea

[Felzenszwalb & Huttenlocher segmentation](./0.Efficient_Graph_Based_Segmentation.md) 같은 저수준 분할을 여러 스케일에서 수행.

이후 색상, 질감, 크기, 공간적 인접성 등을 기준으로 영역(region)들을 계층적(hierarchical)으로 병합.

결과적으로 수천 개의 **object-like 후보 영역(region proposals)**을 생성.

---

Selective search 이전에는 물체가 있을만한 영역을 모두 조사해보는 Exhaustive search 방법이 있었다.

쉽게 말해서, Sliding window + multi-scale search 방식이고, 가능한 모든 위치와 크기의 사각형 윈도우를 만들어서 일일히 분류기 (SVM, CNN 등)에 넣는 방식이다.

이런 방식의 문제점을 해결하기 위해 나온 것이 Selective search이고, 

가능한 모든 영역 대신 segmentation 기반 Region proposal 을 뽑아낸 뒤에, 
Feature 기준으로 작은 영역을 합쳐서 의미 있는 후보만을 남기고, 
이 후보들을 분류기에 넣는 방식이다.