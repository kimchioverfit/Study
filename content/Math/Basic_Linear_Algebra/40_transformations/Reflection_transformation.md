# Reflection Transformation

대칭 변환(reflection transformation)은

벡터나 도형을 어떤 축 또는 직선에 대해 거울처럼 뒤집는 선형 변환이다.

---

## 기본 개념

2차원에서 대칭 변환은 한 축을 기준으로 좌우 또는 상하를 뒤집는 변환으로 볼 수 있다.

- $x$축 대칭: 위아래 반전
- $y$축 대칭: 좌우 반전
- 직선 $y=x$ 대칭: 좌표 교환

대칭 변환은 원점을 고정하므로 선형 변환이다.

---

## 1. $x$축 대칭

점

```math
\begin{bmatrix}
x\\
y
\end{bmatrix}
```

를 $x$축에 대해 대칭시키면

```math
\begin{bmatrix}
x\\
-y
\end{bmatrix}
```

가 된다.

행렬로 쓰면

```math
A =
\begin{bmatrix}
1 & 0\\
0 & -1
\end{bmatrix}
```

즉,

```math
T(\mathbf{x}) = A\mathbf{x}
```

이다.

---

## 2. $y$축 대칭

```math
\begin{bmatrix}
x\\
y
\end{bmatrix}
\rightarrow
\begin{bmatrix}
-x\\
y
\end{bmatrix}
```

행렬은

```math
\begin{bmatrix}
-1 & 0\\
0 & 1
\end{bmatrix}
```

이다.

---

## 3. 직선 $y=x$에 대한 대칭

```math
\begin{bmatrix}
x\\
y
\end{bmatrix}
\rightarrow
\begin{bmatrix}
y\\
x
\end{bmatrix}
```

행렬은

```math
\begin{bmatrix}
0 & 1\\
1 & 0
\end{bmatrix}
```

이다.

---

## 성질

1. 대칭 변환은 길이를 보존한다.
2. 각도를 보존한다.
3. orientation은 뒤집힌다.
4. 행렬식은 보통 $-1$이다.
5. 두 번 적용하면 원래 상태로 돌아온다.

즉,

```math
R^2 = I
```

형태가 된다.

---

## 기하적 의미

대칭축 위의 점은 그대로 유지된다.

대칭축에서 떨어진 점은 축 반대편의 같은 거리 위치로 이동한다.

즉, 축을 기준으로 거울에 비춘 것과 같은 효과다.

---

## 예시

```math
A =
\begin{bmatrix}
1 & 0\\
0 & -1
\end{bmatrix},
\quad
v =
\begin{bmatrix}
2\\
3
\end{bmatrix}
```

이면

```math
Av =
\begin{bmatrix}
1 & 0\\
0 & -1
\end{bmatrix}
\begin{bmatrix}
2\\
3
\end{bmatrix}
=
\begin{bmatrix}
2\\
-3
\end{bmatrix}
```

이다.

즉, $(2,3)$은 $x$축 대칭 후 $(2,-3)$이 된다.

---

## 어디에 쓰이나?

1. 컴퓨터 그래픽스
2. 기하학적 모델링
3. 영상 처리
4. 좌표계 변환
5. 선형 변환의 성질 분석

---

## 관련 문서

- [Linear_transform](./Linear_transform.md)
- [Rotation_transformation](./Rotation_transformation.md)
- [Symmetric_matrix](../20_matrix_types/Symmetric_matrix.md)
