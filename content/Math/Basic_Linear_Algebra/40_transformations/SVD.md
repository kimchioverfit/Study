# SVD

SVD(Singular Value Decomposition, 특이값 분해)는

임의의 행렬 $A$를 세 개의 행렬로 분해하는 방법이다.

```math
A = U \Sigma V^T
```

여기서

- $U$: left singular vectors
- $\Sigma$: singular values를 담은 diagonal matrix
- $V$: right singular vectors

이다.

---

## 왜 중요한가?

eigen decomposition은 보통 정사각행렬에서 다루지만,

SVD는 직사각행렬에도 적용할 수 있다.

즉,

- 데이터 행렬
- 이미지 행렬
- 추천 시스템의 사용자-아이템 행렬

같은 실제 문제에 더 직접적으로 쓰기 좋다.

---

## 구성 요소

행렬 $A \in \mathbb{R}^{m \times n}$ 에 대해

```math
A = U \Sigma V^T
```

라고 하면,

### 1. $U$

```math
U \in \mathbb{R}^{m \times m}
\\
m * m 행렬\ 형태.
```

출력 공간 쪽의 직교기저를 담는다.

```math
(AA^T 의\ eigen\ vector 이기도 하다.)
```

각 열벡터는 left singular vector이다.

---

### 2. $\Sigma$

```math
\Sigma \in \mathbb{R}^{m \times n}
```

대각선에 특이값(singular values)이 들어간다.

```math
\sigma_1 \ge \sigma_2 \ge \cdots \ge \sigma_r \ge 0
```

특이값이 클수록 해당 방향이 더 중요하다고 볼 수 있다.

---

### 3. $V$

```math
V \in \mathbb{R}^{n \times n}
```

입력 공간 쪽의 직교기저를 담는다.

각 열벡터는 right singular vector이다.

```math
A^TA\ 의 eigen\ vector\ 임.
```

---

## eigen value와의 관계

SVD는 다음 두 행렬과 깊게 연결된다.

```math
A^T A,\quad AA^T
```

- $A^T A$의 eigen vector가 $V$
- $AA^T$의 eigen vector가 $U$
- $A^T A$의 eigen value를 $\lambda_i$라 하면, singular value는

```math
\sigma_i = \sqrt{\lambda_i}
```

가 된다.

즉, SVD는 eigen value / eigen vector 개념을 일반 행렬로 확장해서 쓰는 방식이라고 볼 수 있다.

관련 개념:

- [Eigen value](./Eigen_value.md)
- [Eigen vector](./Eigen_vector.md)
- [Eigen decomposition](./Eigen_decomposition.md)

---

## 기하적 의미

SVD는 선형 변환 $A$를 세 단계로 나눠서 본다.

```math
A = U \Sigma V^T
```

1. $V^T$: 입력 좌표계를 회전 또는 반사
2. $\Sigma$: 각 축 방향으로 늘이거나 줄임
3. $U$: 다시 회전 또는 반사

즉, 복잡한 선형 변환도

`회전/반사 -> 축별 스케일링 -> 회전/반사`

로 해석할 수 있다.

---

## 간단한 직관

원 모양 데이터가 있다고 하자.

어떤 선형 변환을 거치면 원이 타원으로 바뀔 수 있다.

이때:

- 타원의 긴 축, 짧은 축 방향은 singular vector
- 각 축 길이는 singular value

로 볼 수 있다.

---

## rank-k 근사

SVD의 매우 중요한 활용 중 하나는 저랭크 근사(low-rank approximation)이다.

```math
A = \sum_{i=1}^{r} \sigma_i u_i v_i^T
```

여기서 큰 특이값 몇 개만 남기면

```math
A_k = \sum_{i=1}^{k} \sigma_i u_i v_i^T
```

처럼 근사할 수 있다.

이렇게 하면 중요한 정보는 유지하면서 데이터 크기를 줄일 수 있다.

---

## PCA와의 관계

PCA는 보통 공분산 행렬의 eigen decomposition으로 설명되지만,

실제로는 중심화된 데이터 행렬 $X$에 대해 SVD를 적용해서도 구할 수 있다.

```math
X = U \Sigma V^T
```

이때:

- $V$의 열벡터: principal directions
- $\Sigma$의 크기: 각 주성분의 중요도와 관련

즉, PCA는 SVD로도 매우 자연스럽게 계산된다.

관련 문서:

- [PCA](./PCA.md)

---

## 어디에 쓰이나?

1. 차원 축소
2. 이미지 압축
3. 노이즈 제거
4. 추천 시스템
5. 문서 검색, latent semantic analysis
6. 의사역행렬(pseudoinverse) 계산

---

## 장점

- 직사각행렬에도 적용 가능
- 수치적으로 안정적
- 차원 축소와 압축에 매우 유용
- 행렬의 구조를 잘 드러냄

---

## 요약

```math
A = U \Sigma V^T
```

- $U$, $V$는 방향 정보
- $\Sigma$는 각 방향의 중요도
- SVD는 일반 행렬을 해석하는 가장 강력한 분해 중 하나
- PCA, 압축, 노이즈 제거 등에 널리 사용됨

---

## 예시

아래와 같은 행렬을 보자.

```math
A =
\begin{bmatrix}
3 & 0\\
0 & 2
\end{bmatrix}
```

이 행렬의 SVD를 구해보자.

### 1. $A^T A$ 계산

```math
A^T A =
\begin{bmatrix}
3 & 0\\
0 & 2
\end{bmatrix}
\begin{bmatrix}
3 & 0\\
0 & 2
\end{bmatrix}
=
\begin{bmatrix}
9 & 0\\
0 & 4
\end{bmatrix}
```

---

### 2. eigen value 계산

```math
\lambda_1 = 9,\quad \lambda_2 = 4
```

singular value는 eigen value의 제곱근이므로

```math
\sigma_1 = \sqrt{9} = 3,\quad \sigma_2 = \sqrt{4} = 2
```

이다.

따라서

```math
\Sigma =
\begin{bmatrix}
3 & 0\\
0 & 2
\end{bmatrix}
```

가 된다.

---

### 3. $V$ 구하기

$A^T A$가 이미 대각행렬이므로 eigen vector는 표준기저이다.

```math
v_1 =
\begin{bmatrix}
1\\
0
\end{bmatrix},
\quad
v_2 =
\begin{bmatrix}
0\\
1
\end{bmatrix}
```

즉,

```math
V =
\begin{bmatrix}
1 & 0\\
0 & 1
\end{bmatrix}
```

이다.

---

### 4. $U$ 구하기

공식

```math
u_i = \frac{Av_i}{\sigma_i}
```

를 사용하면,

```math
u_1 = \frac{A v_1}{\sigma_1}
=
\frac{
\begin{bmatrix}
3 & 0\\
0 & 2
\end{bmatrix}
\begin{bmatrix}
1\\
0
\end{bmatrix}
}{3}
=
\frac{
\begin{bmatrix}
3\\
0
\end{bmatrix}
}{3}
=
\begin{bmatrix}
1\\
0
\end{bmatrix}
```

```math
u_2 = \frac{A v_2}{\sigma_2}
=
\frac{
\begin{bmatrix}
3 & 0\\
0 & 2
\end{bmatrix}
\begin{bmatrix}
0\\
1
\end{bmatrix}
}{2}
=
\frac{
\begin{bmatrix}
0\\
2
\end{bmatrix}
}{2}
=
\begin{bmatrix}
0\\
1
\end{bmatrix}
```

따라서

```math
U =
\begin{bmatrix}
1 & 0\\
0 & 1
\end{bmatrix}
```

이다.

---

### 5. 최종 결과

결국

```math
A = U \Sigma V^T
=
\begin{bmatrix}
1 & 0\\
0 & 1
\end{bmatrix}
\begin{bmatrix}
3 & 0\\
0 & 2
\end{bmatrix}
\begin{bmatrix}
1 & 0\\
0 & 1
\end{bmatrix}
```

이므로,

이 예제에서는

- $U = I$
- $\Sigma = \begin{bmatrix} 3 & 0 \\ 0 & 2 \end{bmatrix}$
- $V = I$

가 된다.

---

### 이 예시에서 볼 수 있는 점

이 행렬은 이미 각 축 방향으로만 스케일링하는 형태이므로,

회전이 필요 없다.

그래서 $U$와 $V$가 모두 항등행렬로 나오고,

스케일 정보만 $\Sigma$에 그대로 들어간다.
