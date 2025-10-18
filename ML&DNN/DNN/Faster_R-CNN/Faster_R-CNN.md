# Faster R-CNN



RPN 은 쉽게말해서, CNN 모델이다. 
어떤 class의 object가 있을법한 위치를 Rect 형태로 추정하는 모델이며, 

Mask R-CNN이나 Faster R-CNN에서는 class 정보는 따로 classification 하고 
Rect내에 Object가 있는지 없는지에 대한 확률값만 이용한다.

상세 내용 추가 필요 

Faster R-CNN 으로 이용할때 보통 RPN 까지 새로 학습하면 오래걸려서 
보통 Backbone으로 가져와서 pretrained 된걸 쓴다.