# Nueral Network example

뉴럴 네트워크의 기본 학습을 위한 샘플 공부 

시작하기에 앞서, 기본적인 전제는 아래와 같다.

Input : Scalar x 
Hidden layer : Neural 1 개(w, b 1 개 쌍), activation funciton은 sigmoid
Ouput layer : y
Loss function : MSE 
Parameter : Hidden layer 내부의 Layer-1에서는 w1, b1이 있다고 가정, Output layer 에서는 w2, b2가 있다고 가정

# Forward

### Hidden layer

$z_1 = w_1 x + b_1$

신경망 학습의 기본이 `선형 → 비선형 → 선형` 의 반복 구조.
에시에서는 1개짜리 뉴런으로 했으므로 위와 같음.
Activation layer 에 들어가기 위해서는 선형구조여야 한다.

### Activation layer 

$a_1 = \partial(z_1) = \frac{1}{1+e^{-z_1}}$

예시에서는 시그모이드 함수 사용.

### Output layer 

예시에서는 활성함수 없이 Linear로 가정.

$y = z_2$
$z_2 = w_2a_1 + b_2$

### Loss function 

예시에서는 MSE를 사용

$L = \frac{1}{2}(y-t)^2$

y는 output이고, t는 prediction이다.

---

신경망 학습의 기본은 Loss function이 최소가 되는 지점을 찾는 것.

$L = \frac{1}{2}(y-t)^2$

위 식을 y에 관해서 미분하자.

신경망 학습은 결국 weight 를 찾는 과정이므로, 

역순으로 보았을 때 가장 먼저 나오는 $w_2$를 구하기 위해서는

y에 관해 미분해줘야 한다.

$\frac{dL}{dy} = y-t$ 

이므로, y = t 가 되는 지점을 찾으면 끝이겠지만,
$즉, y = t = w_2a_1 + b_2$ 이고, 
$w_2$를 구하는 것이 목표이므로, 

$w_2 = \frac{t-b_2}{a_1}$ 를 구하면 끝이라고 생각하겠지만,

문제는 

1. 실제 신경망 학습에서는 여러 데이터를 이용하므로 b, w가 무수히 많다.(데이터 수 만큼의 방정식을 동시에 만족하는 해가 존재하지 않을 수도 있다.)

2. y는 애초에 output layer에서 나온, 비선형 방정식이므로 바로 구할 수 있는 방법이 없다.

**그러므로**, Backpropagation을 통해 y = t에 근접한 지점을 찾기 위해 기울기를 이용하는 것. (Gradient)

$\frac{dL}{dw}$를 구해야한다는 말.

---
이제 구해야 할 목표를 찾았으니 수식을 보자

$\frac{dL}{dw}$를 구하기위해서는 기존의 y식을 쓰자

$ y = w_2a_1 + b_2$를 미분하면 

$ \frac{dy}{dw_2} = a_1 (b는 상수다)$ 

$ \frac{dL}{dy} = \frac{dL}{dw_2} × \frac{dw_2}{dy}= y -t $ 이므로

$\frac{dL}{dw_2} × \frac{1}{a} = y -t$

$\frac{dl}{dw_2} = a_1(y-t)$이다.

최소지점을 찾으려면 기울기가 0인 지점을 찾아야하고,

$w_2$에 대한 기울기가 
- 0보다 크면 왼쪽으로 이동, 
- 0보다 작으면 오른쪽으로 이동해야 한다.

즉, 새로운 $w_2 = (부호) × learning rate × \frac{dL}{dw_2}$ 로 갱신되게 된다. 

이것을 반복하면 신경망 학습.