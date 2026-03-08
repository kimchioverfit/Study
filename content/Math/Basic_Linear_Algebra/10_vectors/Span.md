# Span

생성집합(span)은 어떤 벡터들의 모든 선형결합으로 만들 수 있는 벡터들의 집합이다.

벡터 $v_1, v_2, \dots, v_k$가 있을 때,

```math
\mathrm{span}(v_1, v_2, \dots, v_k)
=
\left\{
a_1 v_1 + a_2 v_2 + \cdots + a_k v_k
\;\middle|\;
a_1, a_2, \dots, a_k \in \mathbb{R}
\right\}
```

로 정의한다.

---

## 의미

span은 주어진 벡터들로 어디까지 만들 수 있는지를 나타낸다.

- 한 벡터의 span: 직선
- 두 개의 독립인 벡터의 span: 평면
- 세 개의 독립인 벡터의 span: 3차원 공간

즉, span은 벡터들이 만들어내는 공간 자체라고 보면 된다.

---

## 예시 1

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

이면

```math
\mathrm{span}(v_1, v_2) = \mathbb{R}^2
```

이다.

왜냐하면 임의의 벡터

```math
\begin{bmatrix}
x\\
y
\end{bmatrix}
=
x
\begin{bmatrix}
1\\
0
\end{bmatrix}
+
y
\begin{bmatrix}
0\\
1
\end{bmatrix}
```

로 표현할 수 있기 때문이다.

---

## 예시 2

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

이면 $v_2 = 2v_1$ 이므로 두 벡터는 같은 방향이다.

따라서

```math
\mathrm{span}(v_1, v_2)
```

는 평면 전체가 아니라 하나의 직선만 만든다.

---

## 생성한다는 말의 의미

벡터 집합 $S$가 어떤 공간 $V$를 생성한다는 것은

```math
\mathrm{span}(S) = V
```

라는 뜻이다.

즉, 그 공간의 모든 벡터를 $S$의 선형결합으로 표현할 수 있어야 한다.

---

## 기저와의 관계

span만으로는 충분하지 않다.

벡터를 많이 넣으면 같은 공간을 생성할 수는 있지만 중복이 생길 수 있다.

그래서 보통은

- 공간을 생성하고
- 서로 선형 독립인

벡터 집합을 찾고 싶다.

그런 집합이 [Basis](./Basis.md)이다.

관련 문서:

- [Linear Independence](./Linear_independence.md)
- [Basis](./Basis.md)
