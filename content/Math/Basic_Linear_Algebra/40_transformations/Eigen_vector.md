# eigen vector & eigen value

eigen  vector 란, 행렬이 변환되어도 그대로 유지되는 벡터를 말한다.

### 예시를 하나 보도록 하자 

```math
A =
\begin{bmatrix}
2 & 0\\
0 & 3\\
\end{bmatrix}

v_1 =
\begin{bmatrix}
1\\
0\\
\end{bmatrix}
이라고 할 때, 
```

```math
Av_1 = 
\begin{bmatrix}
2 & 0\\
0 & 3\\
\end{bmatrix}

\begin{bmatrix}
1\\
0\\
\end{bmatrix} = 

\begin{bmatrix}
2\\
0\\
\end{bmatrix} = 2v_1  이다.
```

이때 2를 eigen value 라고 하고, eigen vector는 v_1이다.

---

### 예시를 하나 더 보도록 하자.

```math
A = 
\begin{bmatrix}
4 & 1\\
2 & 3\\
\end{bmatrix} 가\;있을\;때, 
```

```math
우선은\;det를\;이용해서\;eigen\;vector를\;구해야한다.
```

```math
det(A-λI)=0\\
```

```math
det
\begin{bmatrix}
4 & 1\\
2 & 3\\
\end{bmatrix} = 0
```

```math
(4-λ)(3-λ)-2=0
```

```math
λ^2-7λ+10 = 0
```

```math
λ_1 = 2, λ_2 = 5
```

```math
λ_1 이\;해인\;경우 (A-5I)v=0\\
λ_2 가\;해인\;경우 (A-2I)v=0\\
```

```math
v_1=
\begin{bmatrix}
1\\
1\\
\end{bmatrix}
```

```math
v_2=
\begin{bmatrix}
-1\\
2\\
\end{bmatrix}
```

```math
즉, 

v=
\begin{bmatrix}
1 & -1\\
1 & 2\\
\end{bmatrix} 가\; 된다.

```
---

### 이러한 eigen value & eigen vector를 어디에 쓰는 것일까?

[Eigen decomposition](./Eigen_decomposition.md)

