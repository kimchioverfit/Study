
# 📌 회문 (Palindrome)

### 🕐 시간 복잡도
- 최소 O(N): 전체 문자 확인이 필요

### ✅ 해법 1: 해시맵 이용

```cpp
bool isPalindromeMap(const std::string& s) {
    std::unordered_map<char, int> freq;
    for (char c : s) {
        if (std::isalpha(c)) freq[std::tolower(c)]++;
    }
    int oddCount = 0;
    for (const auto& p : freq) {
        if (p.second % 2 != 0) oddCount++;
        if (oddCount > 1) return false;
    }
    return true;
}
```


### ✅ 해법 2: 비트 벡터 이용 (공간 최적화)

```cpp
bool isPalindromePermutation(const std::string& s) {
    int bitVector = 0;
    for (char c : s) {
        if (std::isalpha(c)) {
            int index = std::tolower(c) - 'a';
            bitVector ^= (1 << index);  // 해당 비트를 XOR 연산으로 토글
        }
    }
    return bitVector == 0 || (bitVector & (bitVector - 1)) == 0;
}
```

#### 🔍 설명

- **bitVector는 int형(32bit)으로 충분**한다. 알파벳은 소문자 기준 26자이므로 32비트 내에 모두 저장 가능한다.
- **초기 상태**는 `00000000 00000000 00000000 00000000`.
- 예를 들어 문자열에 `'b'`가 있다면:
  - `'b' - 'a' = 1` → `1 << 1 = 0b10` → `bitVector ^= 0b10`로 해당 비트를 1로 설정
- 동일한 문자가 다시 등장하면 XOR로 해당 비트가 다시 꺼집니다 (즉, 짝수 번 등장하면 0).
- 결국 **bitVector가 0**이면 모든 문자가 짝수 번 등장한 것.
- 하지만 문자열 길이가 홀수이면 **1개의 문자는 홀수번 등장**해도 회문 가능 → 이때는 `bitVector`에 **1개의 비트만 켜져 있어야 함**.
  - 이를 판별하는 조건이 `bitVector & (bitVector - 1) == 0`. (1비트만 켜져 있으면 참)
  - 이게 어렵다면: 문자열 길이가 홀수면 `bitVector == 1`, 짝수면 `bitVector == 0`을 각각 확인해도 됩니다.
- **시간 복잡도**는 `O(N)`.


```cpp
bool isPalindromePermutation(const std::string& s) {
    int bitVector = 0;
    for (char c : s) {
        if (std::isalpha(c)) {
            int index = std::tolower(c) - 'a';
            bitVector ^= (1 << index);
        }
    }
    return bitVector == 0 || (bitVector & (bitVector - 1)) == 0;
}
```

- 짝수 길이 → 모든 비트가 0
- 홀수 길이 → 하나의 비트만 1일 수 있음
- 시간 복잡도: O(N)
