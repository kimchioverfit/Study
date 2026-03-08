# Eigendecomposition

고유값 분해라고도 한다. 

주로 주성분분석(PCA)나 차원 축소 등에 쓰인다.

아래 예시를 통해 알아보자.

여기서는 R-CNN에 쓰이는 `selective search` 를 이용해 알아보자.

Selective search는 

1. 작은 초기영역을 설정
2. 반복적으로 작은 초기영역을 큰 영역으로 통합
3. 통합된 영역을 바탕으로 ROI 그리기

3가지 프로세스가 있는데, 그 중 초기 영역 선정에 

Felzenszwalb와 Huttenlocher의 Efficient Graph-Based Image Segmentation을 사용할 수 있다. 


### 예시

```math
A = 
\begin{bmatrix}
1 & 2 & 3 & 4 & 5\\
6 & 7 & 8 & 9 & 10\\
\cdots & \cdots & \cdots & \cdots  & \cdots \\
\cdots  & \cdots & \cdots & \cdots & 25\\ 
\end{bmatrix}
```

1. 우선 인접 행렬을 획득하도록 하자. 
    
    (1,1)에서의 adjacency matrix를 구하면, 

    {2,6}(2,1)에서는 {2, 6, 8, 12} 이런 식으로...

    다 구하면 25 x 25 짜리 인접행렬이 생성된다.

2. 유사도를 측정해보자.
    
    ```math
    W_{ij} = 
    exp(-(I_i-I_j)^2/2σ^2I)
    ```
    계산 과정은 생략

3. Results
    
    ```math
    W_{(1\sim 5)(1\sim5)} = 
    \begin{bmatrix}
    0 & 1 & 0 & 0 & 0\\
    1 & 0 & 0.13 & 0 & 0\\
    0 & 0 & 1 & 0  & 1 \\
    \cdots  & \cdots & \cdots & 1 & 0\\ 
    \end{bmatrix}
    ```
    이런 식으로 나온 결과를 보면, 군집화가 되는 것을 볼 수 있다.

    이를 통해서 군집화된 Pixel들을 하나의 Object로서, Segmentation작업할 수 있다.