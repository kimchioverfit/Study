# Faster R-CNN



### RPN

Fast R-CNN 은 selective search 의 느린 속도 문제를 해결하고자 

RPN을 도입한다. 

RPN은 쉽게 말해, Region proposal을 보다 정교하게 추출하기 위해 다양한 크기와 가로세로비를 가지는 bounding box 인 **Anchor box**를 도입한다.



RPN 은 쉽게말해서, CNN 모델이다. 
어떤 class의 object가 있을법한 위치를 Rect 형태로 추정하는 모델이며, 

Mask R-CNN이나 Fast R-CNN에서는 class 정보는 따로 classification 하고 
Rect내에 Object가 있는지 없는지에 대한 확률값만 이용한다.

상세 내용 추가 필요 

Fast R-CNN 으로 이용할때 보통 RPN 까지 새로 학습하면 오래걸려서 
보통 Backbone으로 가져와서 pretrained 된걸 쓴다.