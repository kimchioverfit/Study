# Rotation Transformation

회전 변환(rotation transformation)은

벡터나 도형을 원점을 기준으로 일정 각도만큼 회전시키는 선형 변환이다.

---

## 2차원 회전 변환

2차원에서 각도 $\theta$만큼 반시계 방향으로 회전시키는 행렬은

```math
R(\theta) =
\begin{bmatrix}
\cos\theta & -\sin\theta\\
\sin\theta & \cos\theta
\end{bmatrix}
```

이다.

즉,

```math
\begin{bmatrix}
x'\\
y'
\end{bmatrix}
=
\begin{bmatrix}
\cos\theta & -\sin\theta\\
\sin\theta & \cos\theta
\end{bmatrix}
\begin{bmatrix}
x\\
y
\end{bmatrix}
```

로 표현된다.

---

## 왜 선형 변환인가?

회전 변환은

1. 벡터 덧셈을 보존하고
2. 스칼라배를 보존한다.

또한 원점을 그대로 유지한다.

그래서 회전은 대표적인 선형 변환이다.

---

## 90도 회전 예시

반시계 방향으로 90도 회전하면

```math
R\left(\frac{\pi}{2}\right) =
\begin{bmatrix}
0 & -1\\
1 & 0
\end{bmatrix}
```

이다.

벡터

```math
v =
\begin{bmatrix}
1\\
0
\end{bmatrix}
```

를 회전시키면

```math
Rv =
\begin{bmatrix}
0 & -1\\
1 & 0
\end{bmatrix}
\begin{bmatrix}
1\\
0
\end{bmatrix}
=
\begin{bmatrix}
0\\
1
\end{bmatrix}
```

이다.

즉, $x$축 방향 벡터가 $y$축 방향으로 회전한다.

---

## 180도 회전

```math
R(\pi) =
\begin{bmatrix}
-1 & 0\\
0 & -1
\end{bmatrix}
```

이는 원점을 중심으로 뒤집는 것과 같다.

---

## 성질

1. 길이를 보존한다.
2. 각도를 보존한다.
3. 내적을 보존한다.
4. 행렬식은 $1$이다.
5. 역행렬은 전치행렬과 같다.

즉,

```math
R^{-1} = R^T
```

이고,

```math
R^T R = I
```

를 만족한다.

따라서 회전행렬은 직교행렬이다.

---

## 기하적 의미

회전 변환은 도형의 크기와 모양은 유지한 채,

방향만 바꾸는 변환이다.

즉, 강체 운동(rigid motion)의 대표적인 예라고 볼 수 있다.

---

## 대칭 변환과의 차이

- 회전 변환: orientation 유지
- 대칭 변환: orientation 반전

그래서 회전행렬의 determinant는 $1$이고,

대칭 변환 행렬의 determinant는 보통 $-1$이다.

---

## 어디에 쓰이나?

1. 컴퓨터 그래픽스
2. 로봇공학
3. 물리 시뮬레이션
4. 좌표계 변환
5. 3D 비전

---

## 관련 문서

- [Linear_transform](./Linear_transform.md)
- [Reflection_transformation](./Reflection_transformation.md)
- [SVD](./SVD.md)
