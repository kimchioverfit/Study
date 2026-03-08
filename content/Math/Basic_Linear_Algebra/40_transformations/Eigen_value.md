# Eigen value

고유값(eigen value)은 어떤 행렬이 특정 벡터를 변환할 때, 그 벡터의 방향은 유지한 채 얼마나 스케일되는지를 나타내는 값이다.

행렬 $A$와 0이 아닌 벡터 $v$에 대해

```math
Av = \lambda v
```

를 만족하면,

- $v$: eigen vector
- $\lambda$: eigen value

라고 한다.

---

## 왜 중요한가?

보통 행렬은 벡터의 방향과 크기를 모두 바꾸지만,

eigen vector 방향에 있는 벡터는 방향이 유지되고 크기만 바뀐다.

이때 그 변화량이 eigen value이다.

- $\lambda > 1$: 벡터가 늘어남
- $0 < \lambda < 1$: 벡터가 줄어듦
- $\lambda < 0$: 방향이 뒤집히면서 스케일됨
- $\lambda = 0$: 해당 방향 성분이 사라짐

---

## 고유값은 어떻게 구하나?

고유값은 다음 characteristic equation을 풀어서 구한다.

```math
\det(A - \lambda I) = 0
```

여기서

- $A$: 원래 행렬
- $I$: identity matrix
- $\lambda$: 구하고자 하는 eigen value

이다.

즉, $A - \lambda I$의 determinant가 0이 되는 $\lambda$를 찾으면 된다.

---

## 예시

```math
A =
\begin{bmatrix}
4 & 1\\
2 & 3\\
\end{bmatrix}
```

라고 하자.

그러면

```math
\det(A-\lambda I) = 0
```

```math
\det
\begin{bmatrix}
4-\lambda & 1\\
2 & 3-\lambda\\
\end{bmatrix}
= 0
```

```math
(4-\lambda)(3-\lambda) - 2 = 0
```

```math
\lambda^2 - 7\lambda + 10 = 0
```

```math
(\lambda - 2)(\lambda - 5)=0
```

따라서 eigen value는

```math
\lambda_1 = 2,\quad \lambda_2 = 5
```

이다.

각 고유값에 대응하는 eigen vector는 [Eigen vector](./Eigen_vector.md)에서 구할 수 있다.

---

## 기하적 의미

선형 변환은 공간을 회전, 확대, 축소, 반사할 수 있다.

그런데 어떤 특별한 방향은 변환 이후에도 같은 직선 위에 남는다.

그 방향이 eigen vector이고, 그 방향에서의 확대/축소 비율이 eigen value이다.

---

## 어디에 쓰이나?

1. [Eigen decomposition](./Eigen_decomposition.md)
2. [PCA](./PCA.md)
3. 진동/안정성 해석
4. 그래프 분석
5. 선형 변환의 성질 파악

---

## 요약

```math
Av = \lambda v
```

- eigen value는 특정 방향에서의 스케일 변화량
- $\det(A-\lambda I)=0$으로 구함
- eigen vector와 함께 행렬의 구조를 이해하는 핵심 개념
