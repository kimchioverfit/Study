# Linear Independence

선형 독립(linear independence)은

어떤 벡터 집합 안의 벡터들이 서로 중복되지 않는다는 뜻이다.

즉, 한 벡터를 나머지 벡터들의 선형결합으로 만들 수 없으면 선형 독립이라고 한다.

---

## 정의

벡터 $v_1, v_2, \dots, v_k$에 대해

```math
a_1 v_1 + a_2 v_2 + \cdots + a_k v_k = 0
```

을 만족하는 스칼라 $a_1, a_2, \dots, a_k$가

```math
a_1 = a_2 = \cdots = a_k = 0
```

뿐이라면, 이 벡터들은 선형 독립이다.

반대로 0이 아닌 계수로도 위 식이 성립하면 선형 종속(linearly dependent)이다.

---

## 직관적으로 보면

- 선형 독립: 중복 없는 방향들
- 선형 종속: 이미 있는 방향의 조합으로 표현 가능한 경우

예를 들어 2차원 공간에서 서로 다른 방향의 두 벡터는 보통 선형 독립이다.

하지만 한 벡터가 다른 벡터의 상수배라면 선형 종속이다.

---

## 예시 1: 선형 독립인 경우

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

에 대해

```math
a_1 v_1 + a_2 v_2 = 0
```

이면

```math
a_1
\begin{bmatrix}
1\\
0
\end{bmatrix}
+
a_2
\begin{bmatrix}
0\\
1
\end{bmatrix}
=
\begin{bmatrix}
0\\
0
\end{bmatrix}
```

이므로

```math
a_1 = 0,\quad a_2 = 0
```

밖에 없다.

따라서 선형 독립이다.

---

## 예시 2: 선형 종속인 경우

```math
v_1 =
\begin{bmatrix}
1\\
2
\end{bmatrix},
\quad
v_2 =
\begin{bmatrix}
2\\
4
\end{bmatrix}
```

는

```math
v_2 = 2v_1
```

이므로 선형 종속이다.

실제로

```math
2v_1 - v_2 = 0
```

처럼 0이 아닌 계수로 0벡터를 만들 수 있다.

---

## 왜 중요한가?

선형 독립은 다음 개념들의 핵심이다.

1. [Span](./Span.md)
2. [Basis](./Basis.md)
3. 차원(dimension)
4. rank
5. 연립방정식 해의 구조

즉, 선형 독립은 벡터 공간의 최소 표현을 찾는 기준이 된다.

---

## 행렬과의 관계

벡터들을 열벡터로 가지는 행렬

```math
A = [v_1 \; v_2 \; \cdots \; v_k]
```

를 생각하면,

- 열벡터들이 선형 독립
- 연립방정식 $A\mathbf{x} = 0$의 해가 $\mathbf{x}=0$만 존재

는 같은 말이다.

정사각행렬에서는 이것이

- $\det(A) \neq 0$
- 역행렬 존재

와도 연결된다.

관련 문서:

- [Determinant](../00_foundations/1.Determinant.md)
- [Inverse Matrix](../20_matrix_types/Inverse_matrix.md)

---

## 요약

- 선형 독립: 중복 없는 벡터 집합
- 선형 종속: 어떤 벡터가 다른 벡터들의 조합으로 표현됨
- 0벡터를 만드는 선형결합이 자명해만 가지면 선형 독립
- 기저, 차원, rank의 핵심 개념
