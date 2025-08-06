# Backbone

주된 feature extractor

일반적으로 CNN, Transformer 기반임.

학습이 잘 된 사전 학습 가중치를 이용하기도 한다. 

예를 들어, resnet50_fpn 모델을 로드했다고 가정하자.

이 모델의 정확도를 향상하기 위해서는 아래와 같은 방법이 요구된다

1. 백본 교체
2. 데이터셋 품질 향상
3. 데이터 증강
4. 하이퍼 파라미터 튜닝
5. 손실 함수 개선
6. ROI 조정
7. Pretrain, fine tuning 전략
8. Post-processing
9. Ensemble 기법 (여러 모델 예측 결과 조합)
10. 학습 스케쥴 및 에포크 조절

등등의 방법이 있는데, 1을 적용해보자


resnet50_fpn 모델은 기본적으로 50 layer가 있다.

resnet101 모델로 교체하면, 101layer을 가진 모델이므로 백본이 훨씬 깊어지고 복잡해짐 (느리겠지만 성능향상)

```
입력 이미지
   ↓
[Backbone]          ← ResNet + FPN  ← 여기만 바꾸는 것
   ↓
[RPN]               ← Region Proposal Network
   ↓
[RoI Align]         ← Region-wise Feature Extraction
   ↓
[Box Head]          ← 클래스/좌표 예측
[Mask Head]         ← 마스크 예측
```
**백본을 바꾼다**는 것은 모델 전체를 바꾸는 게 아니라,

입력 이미지를 특징 벡터(feature map)로 변환하는 

초기 부분(CNN feature extractor)만 바꾸는 것이다.

위 프로세스를 참고하자. 

그런데 만약 사전 학습 가중치를 불러오지 않고 백본만 바꾸면 패턴 학습을 새로해야하는것이므로

웬만하면 사전 학습 가중치를 불러오는 것이 낫다. (데이터가 많거나 하면 굳이 안불러도 되긴 함)


Mask R-CNN 같은 2단계 객체 검출 모델은 모듈화 설계 되어 있음

Backbone과 RPN/Head는 분리된 구조이므로, 서로 독립적으로 교체 가능하다.


