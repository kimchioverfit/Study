# 벡터화 (Flattening)란?

벡터화란 **2차원 또는 다차원 배열(이미지 등)**을 **1차원 벡터 형태로 변환**하는 작업입니다.  
딥러닝 모델, 특히 **완전연결층(Dense Layer)**에 입력으로 넣기 위해 필요한 전처리 단계입니다.


⚠️ **항상 쓰는 것은 아니고**, <u>MLP (다층 퍼셉트론), FC layer 계열 입력용</u>으로 쓰는 것임.

---

## 🧮 수학적 표현

예를 들어, \( X \in \{0,1\}^{H \times W} \) 인 바이너리 이미지를 다음과 같이 1D 벡터로 변환합니다:

```math
x \in \{0,1\}^{H \cdot W}
```

즉,

```math
x = \text{flatten}(X)
```

---

## 📌 예시: 3×3 바이너리 이미지

원래 이미지 행렬:

```math
X =
\begin{bmatrix}
1 & 0 & 1 \\
0 & 1 & 0 \\
1 & 0 & 0
\end{bmatrix}
\in \{0,1\}^{3 \times 3}
```

벡터화 결과 (행 우선 방식, row-major):

```math
x =
\begin{bmatrix}
1 \\
0 \\
1 \\
0 \\
1 \\
0 \\
1 \\
0 \\
0
\end{bmatrix}
\in \{0,1\}^9
```

---


## 🔄 주의점

- 대부분의 딥러닝 프레임워크는 기본적으로 **행 우선(row-major)** 방식으로 flatten 처리합니다.
- **CNN 구조**에서는 보통 `Conv → Pooling` 후 `Flatten → Dense` 순서로 사용됩니다.
