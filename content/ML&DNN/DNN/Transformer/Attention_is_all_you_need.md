# Attention is all you need (Transformer)

트랜스포머 구조가 처음 등장한 논문

### 1. 목표

RNN이나 CNN 없이, 오직 어텐션 메커니즘만으로 시퀀스-투-시퀀스(seq2seq) 문제 해결하기.
번역(translation), 요약(summarization), 질의응답 등 다양한 NLP 작업에 적용 가능.

---

### 2. 기존 접근법의 문제점

| 방식         | 문제점                                                 |
| ---------- | --------------------------------------------------- |
| RNN / LSTM | 순차 처리로 인해 병렬화 어려움, 긴 문장 기억 어려움 (vanishing gradient) |
| CNN        | 병렬화는 가능하나, 문맥을 장기적으로 파악하기 어려움                       |

---

### 3. 핵심 아이디어: 트랜스포머 (Transformer)

🔥 "시퀀스 모델링은 오직 Attention만으로도 충분하다!"

Self-Attention을 사용해 입력의 모든 토큰 간 관계를 계산함.

병렬 처리가 가능하므로, 학습 속도가 빠르고 문맥 파악이 뛰어남.

['트랜스포머의 병렬 처리 구조와 기존의 한계']()

---

### 4. 트랜스포머 구조

[입력 임베딩 + 위치 임베딩] → 인코더 × N → 디코더 × N → 출력

인코더(Encoder): 입력 시퀀스를 처리하여 문맥 정보를 압축함

디코더(Decoder): 인코더 정보를 바탕으로 출력 시퀀스를 생성

---

### 5. 핵심 구성 요소
✅ Self-Attention
- 입력 시퀀스 내의 각 단어가 **다른 모든 단어들과의 관계(중요도)**를 계산
- 관계를 계산하는 방식:

$\text{Attention}(Q, K, V) = \text{softmax}\left( \frac{QK^\top}{\sqrt{d_k}} \right)V$

- Q, K, V: Query, Key, Value 행렬 (입력에서 선형 변환을 통해 얻음)

✅ Multi-Head Attention
- 여러 개의 Self-Attention을 병렬적으로 수행하여 다양한 관계 학습

✅ Positional Encoding
- 순서 정보를 보존하기 위해, 입력 벡터에 사인/코사인 기반 위치 인코딩 추가

✅ Feed Forward Network
- 각 토큰별로 독립적으로 처리되는 두 층짜리 완전연결 신경망

✅ Layer Normalization + Residual Connection
- 학습 안정성과 성능 향상을 위해 적용




###

이 아래는 내가 다시 정리해야함 


###
# 📘 Transformer 전체 구조 정리 (Markdown Version)

## 1. 개요
이 문서는 Transformer 모델(Attention Is All You Need)을 **입력 문장 → 토큰화 → 임베딩 → Q/K/V 생성 → Self-Attention → Multi-head → Encoder/Decoder 구조**까지 **순서대로** 정리한 설명서이다.

---

# 2. 입력 처리: Tokenizer → Token ID

## 2.1 문장 입력
예시:
```
나는 학교에 간다
```

## 2.2 토큰화(Tokenization)
SentencePiece/BPE 기반으로 문장을 토큰 단위로 분할:
```
["나", "##는", "학교", "##에", "간", "##다"]
```

## 2.3 토큰 → 정수 ID 매핑 (Vocabulary)
토크나이저는 사전(vocabulary)을 보유하며 각 토큰을 정수 ID로 변환한다.

| Token | ID |
|-------|----|
| 나 | 102 |
| ##는 | 450 |
| 학교 | 630 |
| ##에 | 231 |
| 간 | 901 |
| ##다 | 250 |

> **ID는 의미가 없다.**  
> 의미는 임베딩 레이어가 학습한다.

---

# 3. 임베딩: Token ID → N차원 벡터

## 3.1 임베딩 레이어의 정체
임베딩 레이어는 크기가 다음과 같은 거대한 행렬:
```
[vocab_size × embedding_dim] = W
```
예:
```
(50,000 × 512)
```

## 3.2 변환 방식
토큰 ID = 임베딩 테이블의 row index.

예:  
토큰 “나”(ID=102) → `W[102]` (512차원 벡터)

즉:
```
Token ID → Lookup → d_model 차원의 벡터
```

## 3.3 사람이 만드는가?
- Vocabulary 는 사람이 정의  
- **임베딩 행렬 W의 값은 학습으로 자동 생성**

---

# 4. Positional Encoding

Transformer는 RNN 구조가 아니라 순서를 모름 → 위치 정보를 더해줌.

입력 =  
```
Embedding + PositionalEncoding
```

---

# 5. Self-Attention: Q, K, V 생성

## 5.1 입력 행렬 X
토큰 수 = T  
임베딩 차원 = d_model

```
X = [x1, x2, ..., xT]  (T × d_model)
```

## 5.2 Q/K/V는 어떻게 만들어지나?
선형 변환 3개로 생성:

```
Q = X W_Q
K = X W_K
V = X W_V
```

각각:
```
W_Q, W_K, W_V ∈ ℝ^(d_model × d_k)
```

> Q/K/V는 “토큰을 3등분하는 것”이 아니라,  
> **X에 다른 가중치를 곱해 3개의 표현을 만든 것**.

---

# 6. Self-Attention 계산 과정

## 6.1 점수 계산 (Similarity)
```
Scores = Q Kᵀ  / sqrt(d_k)
```
→ 크기: (T × T)

## 6.2 Softmax
```
AttentionWeights = softmax(Scores)
```

## 6.3 V에 가중합
```
AttentionOutput = AttentionWeights × V
```

즉, 토큰 간 “누가 누구를 얼마나 참고할지” 계산.

---

# 7. Multi-Head Attention

## 7.1 여러 헤드를 쓰는 이유
- 서로 다른 표현 공간에서 관계를 학습  
- 다양한 패턴/의미/관점을 포착  

## 7.2 구조
```
head_i = Attention(Q_i, K_i, V_i)
MultiHead = Concat(head_1, ..., head_h) W_O
```

---

# 8. Position-wise Feed-Forward Network (FFN)
각 토큰의 벡터에 대해 독립적으로 적용되는 2-layer MLP.

```
FFN(x) = max(0, xW1 + b1) W2 + b2
```

---

# 9. Encoder 구조 (N회 반복)

한 블록:
```
(1) Multi-Head Self-Attention
(2) Add & LayerNorm
(3) Feed-Forward Network
(4) Add & LayerNorm
```

전체 인코더:
```
Input → (EncoderBlock × N) → Output
```

---

# 10. Decoder 구조 (N회 반복)

Decoder는 autoregressive 이므로 **Masked Self-Attention** 사용.

한 블록:
```
(1) Masked Multi-Head Self-Attention
(2) Add & LayerNorm
(3) Encoder-Decoder Attention
(4) Add & LayerNorm
(5) Feed-Forward Network
(6) Add & LayerNorm
```

전체 디코더:
```
TargetInput → (DecoderBlock × N) → Output
```

---

# 11. 출력 단계 (Decoder → Softmax)
디코더의 출력에 선형 변환 + Softmax 적용하여 다음 토큰 확률 예측.

```
P(token | previousTokens) = softmax(W_out · h)
```

---

# 12. 전체 프로세스 요약 (한 줄)

> **문장 → 토큰화 → Token ID → 임베딩 → Q/K/V → Self-Attention → Multi-head → FFN → (반복) → Decoder → Softmax → 다음 단어 예측**

---

# 13. 전체 구조 그림(텍스트 버전)

```
Input Sentence
    ↓
Tokenizer
    ↓
Token IDs
    ↓
Embedding + Positional Encoding
    ↓
[Encoder Block × N]
    ↓
Encoder Output
    ↓
[Decoder Block × N]
    ↓
Softmax
    ↓
Token Prediction
```
