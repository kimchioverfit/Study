
# To do List

순서는 나중에 정리

1. 1998 – LeNet-5
논문: Gradient-Based Learning Applied to Document Recognition
연구자: Yann LeCun 등.
기여:
최초의 CNN(Convolutional Neural Network) 모델로, 손글씨 숫자(MNIST 데이터셋) 인식에서 사용.
CNN 아키텍처(CNN의 기본 구성요소인 컨볼루션, 풀링, 플래튼 레이어 등)를 최초로 체계적으로 정의.
현대의 딥러닝 비전 모델의 기초를 닦은 모델.
2. 2012 – AlexNet
논문: ImageNet Classification with Deep Convolutional Neural Networks
연구자: Alex Krizhevsky, Ilya Sutskever, Geoffrey Hinton
기여:
ImageNet Large Scale Visual Recognition Challenge (ILSVRC)에서 압도적인 성능 향상(Error Rate: 26.2% → 15.3%).
ReLU 활성화 함수와 Dropout 기법 도입.

3. GPU/DSP/NPU architectures 샘플 구현 

4. 병렬처리 개선 - 단순 Threading으로는 가장 많은 시간을 쓰는 inference 속도를 개선하기 힘들듯 -python의 경우에는 GIL (Global Interpreter Lock) 때문에 그러함 그리고, https://seokhyun2.tistory.com/44 공부 

5. Resnet50

6. 템플릿과 컴파일타임 연관성 공부
mask2former 로 roi 잡는 모델 구현 - SegFormer, MaskFormer, Segmenter, DPT모델로 세그멘테이션 하기
논문을 트레이닝 코드로 변환하는거 연습

함수포인터 - typedef 이용한 예제 만들어보면서 연습

path.glob할때 generator소모되는거 까먹었음
ThreadPoolExecutor


실시간 추론, 배포 스케일
GCP, Beam, BigQuery -개인 프로젝트라도 GCP 기반 ML 파이프라인 구성해보기


vector insert, erase
c++ 삼항연산자
md파일로 이미지관리 - 도전볼
반지 찾기
ballseg 정지기능 추가
c++ version으로 문서화까지
docker공부하자