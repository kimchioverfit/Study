# ⚖️ 크라머의 법칙 (Cramer's Rule)

## ✅ 정의

크라머의 법칙은 정방행렬로 이루어진 선형 연립방정식의 해를 행렬식(determinant)을 이용하여 직접 계산하는 방법입니다.

다음과 같은 선형 방정식이 주어졌을 때:

A · x = b


- A: n × n 정방행렬 (계수 행렬)
- x: 미지수 벡터
- b: 상수 벡터

해 \( x_i \)는 다음 공식으로 계산됩니다:

x_i = det(A_i) / det(A)


- A_i: A의 i번째 열을 b 벡터로 대체한 행렬
- det(A): A의 행렬식
- 단, det(A) ≠ 0 이어야 함

---

## 🧮 예제

다음 연립방정식을 크라머의 법칙으로 풀어봅니다:

2x + 3y = 8
4x - y = 2


### ▶ 1. 계수 행렬 A와 상수 벡터 b

A = | 2 3 |
| 4 -1 |

b = | 8 |
| 2 |


---

### ▶ 2. det(A) 계산

det(A) = 2×(-1) - 3×4 = -2 - 12 = -14

---

### ▶ 3. A₁: 첫 번째 열을 b로 교체

A₁ = | 8 3 |
| 2 -1 |

det(A₁) = 8×(-1) - 3×2 = -8 - 6 = -14


---

### ▶ 4. A₂: 두 번째 열을 b로 교체

A₂ = | 2 8 |
| 4 2 |

det(A₂) = 2×2 - 8×4 = 4 - 32 = -28


---

### ▶ 5. 해 구하기

x = det(A₁) / det(A) = -14 / -14 = 1
y = det(A₂) / det(A) = -28 / -14 = 2


---

## ✅ 최종 해

x = 1
y = 2


---

## ⚠️ 조건

- A는 정방행렬이어야 함 (n × n)
- det(A) ≠ 0 이어야 해가 유일하게 존재
- 고차원에서는 비효율적 (계산 복잡도 ↑)

---

## 🧠 활용 예

- 작은 규모의 선형 방정식 해석
- 역행렬을 사용하지 않고 해 구할 수 있음
- 이론적 설명이나 증명에서 자주 사용됨


