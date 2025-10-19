# Mask R-CNN

내가 자주 사용하는 Mask R-CNN에 대한 정리 


우선, Mask R-CNN 의 기본 구조에 대해 알아보자.

기본적으로 3개의 모델(또는 5개라고 보기도)이 합쳐진 구성이다.

1. Feature extractor
2. RPN (Region Proposal Network)
3. ROI Heads (Box classification, Box Regression, Mask head)
+ ROI Align (연산 모듈)

이렇게 구성되어 있고, 핵심 기술은 [Faster R-CNN](3.Faster_R-CNN.md) 과 유사하다. 

