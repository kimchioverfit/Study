# R-CNN

### Main idea

1. [Selective Search](./1.Selective_search.md)로부터 수천 개의 region proposals을 얻음.

2. 각 proposal을 CNN(당시 AlexNet)에 넣어 feature 추출.

3. SVM으로 객체 분류, 회귀(regression)로 bounding box refinement.

---
### Process

<p align="center">
<img src="../../../imgs/Selective_search_1.png" alt="0-3" width="500"/>
</p>

1. 원본 이미지로부터 각각의 Object 들이 1개의 개별 영역에 담길 수 있도록 수 많은 영역들을 생성

    (Object 놓치지 않기 위해 Oversegmentation 수행)

2. 알고리즘에 따라 유사도가 높은 것들을 하나의 Segmentataion 영역으로 합쳐준다.

    <p align="center">
    <img src="../../../imgs/Selective_search_2.png" alt="0-3" width="500"/>
    </p>

    R = r1, ... rn - 최초 segmentation을 통해서 나온 초기 n개의 후보 영역들 

    S - 영역들 사이의 유사도 집합

    - 색상, 무늬, 크기, 형태를 고려하여 각 영역들 사이의 유사도를 계산
    - 유사도가 가장 높은 ri와 rj 영역을 합쳐 새로운 rt 영역을 생성
    - ri와 rj 영역과 관련된 유사도는 S 집합에서 삭제
    - 새로운 rt 영역과 나머지 영역의 유사도를 계산하여 rt의 유사도 집합 St 생성
    - 새로운 영역의 유사도 집합 St와 영역 rt를 기존의 S,R 집합에 추가


3. 2번 과정을 반복하여 최종 후보영역 도출 

<p align="center">
  <img src="../../../imgs/Selective_search_3.png" alt="0-3" width="500"/>
</p>
    이렇게 나온 최종 후보 영역들에 대해서 CNN을 통한 Classification & Bounding box regression 수행하면 
    Object detection이 수행되는 것임. 
    이 과정이 R-CNN 이라고 보면된다.

---


참조 https://developer-lionhong.tistory.com/31#google_vignette