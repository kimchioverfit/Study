
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

NPU란 ?

Neural Processing Unit
딥러닝에서 사용하는 행렬 연산, Convolution 연산 등을 초고속, 저전력으로 처리하도록 만든 전용 Processor.

CNN, RNN, Transformer 같은 신경망 연산 

GPU는 병렬코어로 병렬연산 최적화라면 NPU는 아예 Tensor 를 타겟으로 회로설계한거임. 구체적 내용은 추가 검색 필요 

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

TODO


9. ptr 실습
10. 커널함수 확인
11. TLS 공부

15. cuda 연습

21. cv::cuda::GpuMat
22. template matching 점수 기준에 관해..

25. multiprocessing이 spawn 방식?
26. 전략	효과
27. model.half()	VRAM 사용량 절반
28. inference_mode()	gradient 비활성화 → 메모리 감소
29. torch.compile() (PyTorch 2.x)	연산 최적화로 속도 향상
30. ONNX + TensorRT 변환	추론 속도 2~5배, VRAM 절감

표준 연산(Operation) 집합 정의
ONNX에는 어떤 레이어를 어떻게 표현할까?가 표준화 되어 있어서 서로 다른 프레임워크에서도 같은 의미의 모델을 주고받을 수 있음
(Conv, BatchNorm, ReLU, MatMul 등)

ONNX Runtime
ONNX형식의 모델을 실행하기 위한 엔진이 ONNX Runtime임
CPU, GPU(CUDA), TensorRT, DirectML, OpenVINO, Arm NN, NPU vendor backend 등 다양한 HW지원함

ONNX 파일 전체 구조
계산 그래프(graph) + 연산 노드(node) + 텐서(weight) + 메타데이터 를 모두 프로토버퍼(Protobuf)형식으로 저장한 파일임

# 정리를 좀 다시해야할것 같음 특시 Object detection & segmentation쪽

새로 알게된 사항
1. Libtorch pre build 가져와서 사용할 때, VS2022 에서 build되었기 때문에 cmake 사용 시 오류 발생가능성에 유의
2. cuda 를 프로젝트에 넣기위해서는 C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Microsoft\VC\v160\BuildCustomizations 이런 경로에다가 CUDA 11.8.props,CUDA 11.8.targets, CUDA 11.8.xml,Nvda.Build.CudaTasks.v11.8.dll 이런 파일들을 C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\extras\visual_studio_integration\MSBuildExtensions에서 찾아서 복사해줘야함
3. nvToolsExt3 관련하여, 지원이 중단된것 같음. 자세히 찾아보면 내용 나옴.  어떻게 해결 ? -> 12.1깔아준다음 11.8에서 해당부분만 따로 설치
4. createInferenceInstance함수에서 a function declared 'dllimport' may not be definedC/C++(904) 2019에서는 에러나는데 cpu version 2022에서는 에러안남
5.  dumpbin /EXPORTS path 라는 명령어를 배웠음. 이거쓰면 DLL API볼수있음 . developer for visual stduio cmd인가 이딴걸로 검색하면됨
6.  std::string ImgDir = R"(D:\drawgrids\acf_dll_test\build\Release\sample)"; 이렇게 쓰면 pyrhon에서 r쓰는거랑 비슷하게 가능
7.  인터페이스는 vitual 이라서 vtable참조, 인터페이스가 매칭되지않으면 vptr때문에 동작은 하는데, 다른 함수가호출되거나할수있음
8.  log같은 함수를 만들어서 쓸 때, 비트제한때문에 근사값 발생같은거 조심해야함
9.  


# Pytorch issue 관련

일단, more than one operator > build error (MSVC)

GCC에서는 문제보고가 안됐는데, 원래는 GCC에서도 문제가되어야할것같음

-> Overloading 문제

참고로 확실히 알고 넘어가야하는거

- template 는 Compile 타임에 정해진다는건 정확하게 말하자면, 
Compile time에 여러 Version을 만들어놓고, Runtime에 호출하는거임.

어찌됐건, 


```cpp
AT_DISPATCH_FLOATING_TYPES_AND_HALF(input.scalar_type(), "roi_pool_forward", [&] {
    roi_pool_forward_kernel_impl<scalar_t><<<blocks, threads>>>(...);
});
```
이런 매크로 코드가 있음.

input.scalar_type()은 런타임에 float/half/double 중 하나가 들어오는 “데이터 타입(enum)”

아래는 매크로 내부임 (pytorch/torch/include/ATen/Dispatch.h)


```cpp
#define AT_DISPATCH_FLOATING_TYPES_AND_HALF(TYPE, NAME, ...) \
  AT_DISPATCH_SWITCH(                                        \
      TYPE, NAME, AT_DISPATCH_CASE_FLOATING_TYPES_AND_HALF(__VA_ARGS__))

#define AT_DISPATCH_SWITCH(TYPE, NAME, ...)                                 \
  [&] {                                                                     \
    const auto& the_type = TYPE;                                            \
    constexpr const char* at_dispatch_name = NAME;                          \
    /* don't use TYPE again in case it is an expensive or side-effect op */ \
    at::ScalarType _st = ::detail::scalar_type(the_type);                   \
    RECORD_KERNEL_FUNCTION_DTYPE(at_dispatch_name, _st);                    \
    switch (_st) {                                                          \
      __VA_ARGS__                                                           \
      default:                                                              \
        TORCH_CHECK_NOT_IMPLEMENTED(                                        \
            false,                                                          \
            '"',                                                            \
            at_dispatch_name,                                               \
            "\" not implemented for '",                                     \
            toString(_st),                                                  \
            "'");                                                           \
    }                                                                       \
  }()
```

AT_DISPATCH_SWITCH는 switch (TYPE) 블록을 만들어주는 매크로임.

즉, 내부적으로 

```cpp
switch (TYPE) {
  // case들 (밑의 CASE 매크로에서 생성)
  default: 에러
}
```

이렇게 돌아가는 형태인거임

그다음, 

```cpp
#define AT_DISPATCH_CASE_FLOATING_TYPES_AND_HALF(...)   \
  AT_DISPATCH_CASE(at::ScalarType::Double, __VA_ARGS__) \
  AT_DISPATCH_CASE(at::ScalarType::Float, __VA_ARGS__)  \
  AT_DISPATCH_CASE(at::ScalarType::Half, __VA_ARGS__)

#define AT_DISPATCH_CASE(enum_type, ...) \
  AT_PRIVATE_CASE_TYPE_USING_HINT(enum_type, scalar_t, __VA_ARGS__)

#define AT_PRIVATE_CASE_TYPE_USING_HINT(enum_type, HINT, ...)                 \
  case enum_type: {                                                           \
    AT_PRIVATE_CHECK_SELECTIVE_BUILD(enum_type);                              \
    using HINT [[maybe_unused]] = c10::impl::ScalarTypeToCPPTypeT<enum_type>; \
    return __VA_ARGS__();                                                     \
  }
```

이건 Case들을 만들어주는 함수임 

Double, Float, Half에 대해서 분기만들어주는 중 
(half : half-precision float)

즉, 전체 과정을 이야기해보면

✅ 컴파일 타임에 float/double/half 버전은 전부 인스턴스화되고

✅ 런타임에는 input.scalar_type()에 맞는 case만 실행


---
### Solution

```cpp
using acc_t = at::opmath_type<T>;
acc_t maxval = is_empty ? acc_t(0) : -std::numeric_limits<acc_t>::infinity();
const acc_t val = static_cast<acc_t>(offset_input[i]);
if (val > maxval) { maxval = val; maxidx = i; }
```

위와 같이 자동 승격을 적용하면 나음.

---
코드 설명
```cpp
at::opmath_type<T>
```
연산(accumulation)용 승격 타입을 고르는 메타함수

대표적인 매핑은 대략 다음과 같음.

Half/BFloat16 → float (연산 정확도·안정성 확보)

float → float, double → double

정수형(int8/uint8/int16/int32) → 보통 int64_t (합산 시 오버플로우 여유)

복소형은 대응하는 실수부 승격에 맞춰 복소 타입

즉, 커널 내부에서 비교/누적 등 연산은 더 안정적인 타입 acc_t로 수행한다는 말임

---


왜 승격하나 (계산 측면)

1. 정밀도

    FP16: 유효비트 ~11bit(가수 10 + 숨은 1)

    BF16: 유효비트 ~8bit(가수 7 + 숨은 1)

    FP32: 유효비트 24bit
    → 누적/비교를 16비트로 하면 동률 비교, 작은 차이 소실, tie-break 흔들림 발생가능
    
    FP32로 올리면 ULP 여유가 커져 순위/최댓값 판단이 안정적.

2. 누적 오차 축적 방지

    ROI Pool처럼 “최댓값 비교”도 반복 비교이기 때문에, 
    
    16비트 그대로 두면 라운딩 오차로 인해 max 선택이 뒤틀릴 수 있음 
    
    FP32로 비교하면 이런 리스크가 사실상 사라짐.

3. 오버플로/언더플로

    BF16은 지수 폭이 커서 오버플로엔 강하지만 정밀도는 낮음.

    FP16은 정밀도는 BF16보다 낫지만 지수 폭이 좁아 범위가 작음.

    비교·누적을 FP32로 하면 두 포맷의 각 단점을 회피

---

Overload 해석 관점

오버로드 해석은 대략 이런 순서로 진행

후보 집합 만들기: 빌트인 >와 사용자 정의 operator>(ADL 포함) 등

적합(viable) 후보 고르기: 각 피연산자에 적용 가능한 변환이 있는가

각 후보에 대해 암시적 변환 시퀀스의 등급을 매겨 서열 비교

정확일치 > 승격 > 표준변환 > 사용자정의변환 > …

하나가 나머지보다 “더 낫다”고 판정되면 그걸 택하고, 서열이 동률이면 모호

위의 A/B는 **모두 “사용자정의변환 한 번”**이 들어감

(한쪽은 LHS에서, 한쪽은 RHS에서).

그래서 

3 단계에서 동률, 

4 에서 모호 → 컴파일 에러


# PC Performance

- Disk 관련 
  - SATA 
  - NVMe
    - 2개 드라이브 분리 추천하는 이유 -> 확인 필요하긴 함
    - 병렬 Queue구조  
  - HDD

PCI/PCIe
- x4, x8, x16 등등의 대역폭에 관한 내용

PCI : 병렬 방식으로 여러 비트를 여러 선으로 전달하는 방식 (오래돼서 느림)

PCIe :  메인보드에서 고성능 장치들을 연결하는 초고속 통신 슬롯/규격
(메인 보드의 고속 전용 도로, LAN, USB, SATA 보다 훨씬 빠르고 지연시간도 낮음)
(참고로 요새 나오는 i9 CPU 호환되는 보드들이나 SBC 등에는 PCI 지원안하는 경우가 많다)


PCIe 슬롯 종류

| 표기           | 레인 수 | 쓰는 장치               |
| ------------ | ---- | ------------------- |
| **PCIe x1**  | 1레인  | 사운드카드, USB카드 등      |
| **PCIe x4**  | 4레인  | NVMe SSD, 일부 네트워크카드 |
| **PCIe x8**  | 8레인  | 서버 장치, 고급 RAID 카드   |
| **PCIe x16** | 16레인 | **그래픽카드(주로 이거)**    |

레인이 많을수록 대역폭도 증가하므로 속도도 빠름.

DAQ

SBC(Mainboard) : 보통 산업용으로 사용되는 메인보드같은거. 
슬롯확장을 위해서 백플레인과 결합해서 사용하기도 함.

CPU 
- vectorize (CPU벡터화) 
  - AVX/AVX2/AVX-514 같은 SIMD 명령어로 8/16/32개 데이터 동시 처리 가능
  - numpy 의 dot(), FFT는 내부적으로 이 벡터화 연산을 강하게 사용.
  - 대규모 연산 시 CPU Vector unit이 포화된다. 

- cache 구조 (컴구 내용 복습 필요)
  - L1 cache : 매우 빠르지만 매우 작음 
  - L2 cache : 중간 크기
  - L3 cache : 크고 느림
  - DRAM : 훨씬 더 느림 (cache miss 시 수십~수백 ns 지연)
대규모 연산 시 캐시보다 큰 데이터를 처리하므로 DRAM 대역폭을 많이 쓰고, DRAM에서 데이터를 계속 끌어오게되어서 지연이 늘어남 

CPU는 순차접근 (Sequential) 을 빠르게 처리 가능함. (Prefetcher가 미리 데이터를 읽어놓는다)

랜덤 접근은 매 접근마다 주소가 바뀌므로, prefetcher가 무용지물이고, TLB miss가 증가한다. 
(TLB miss??)
그래서 page table walk 가 필요하고, DRAM 왕복으로 인해 지연이 발생한다. 

Random page walk 
- 메모리 페이지마다 페이지 테이블룩업 필요
- 페이지 테이블이 캐시에 없으면 4단계 page walk
- 이 과정이 누적되면 CPU pipeline stall 발생으로 성능 저하

CPU와 메모리 대역폭
- CPU가 아무리 빨라도 메모리에서 데이터를 빠르게 공급하지 못하면 Core는 idle상태
- 대규모 연산 시 병목은 대부분 메모리 대역폭 문제
  - DDR4/DDR5는 CPU대비 느림. 그래서 `메모리 접근 패턴`이 성능의 절반 이상 결정


P Core
- CPU안에 있는 코어 종류, 요새는 P Core + E Core로 구성한다.
- 무거운 연산은 주로 P Core가 함. (P Core는 1개당 2Thread, E Core는 1개당 1Thread)


---

행렬연산 np.dot의 내부 동작
- BLAS 라이브러리 (OpenBLAS, MKL)실행됨
- CPU는 A,B 블록을 cache에 맞춰 tilting
- AVX 벡터 연산으로 병렬 곱셈
- 결과 캐시 저장
일련의 과정으로 CPU연산 자체는 빠른데 메모리 이동으로 병목이 발생할 수 있음.


FFT(np.fft.rfft) 동작 원리
- FFT는 O(NlogN)알고리즘
  - 배열을 재귀적으로 반 나누고
  - 각각에 복소수 회전 적용
  - 마지막에 합친다
  - > 매우 많은 random-access-like 패턴이 존재한다
  - > CPU캐시 효율이 낮고 메모리 바운드 경향이 강함.


---

Grabber
- 산업용 카메라 전용 영상 수신장치 (CPU대신 받아주는 거임. CPU는 초당 1~5GB데이터를 받으면 병목생기니까)
- PCIe x4, x8, x16등의 고대역폭 이용 -> 아주 빠름

Grabber는 메모리 대역폭도 요구한다.

카메라 -> DMA -> RAM -> CPU 연산 이므로, 
DDR4 보다는 DDR5가 훨씬 유리 

