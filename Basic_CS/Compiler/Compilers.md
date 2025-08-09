

| 컴파일러      | 언어용    | 설명                                     |
| --------- | ------ | -------------------------------------- |
| `gcc`     | C 전용   | GNU C Compiler (C 전용, C++ 표준 라이브러리 없음) |
| `g++`     | C++ 전용 | GNU C++ Compiler (C++ 표준 라이브러리 자동 포함)  |
| `clang`   | C 전용   | LLVM 기반 C 컴파일러 (macOS 기본 탑재)           |
| `clang++` | C++ 전용 | LLVM 기반 C++ 컴파일러 (C++ 라이브러리 포함)        |

| 항목      | GNU (GCC)    | LLVM (Clang)       |
| ------- | ------------ | ------------------ |
| 주 개발 주체 | FSF          | Apple/LLVM Project |
| 주요 컴파일러 | `gcc`, `g++` | `clang`, `clang++` |
| 라이선스    | GPL          | BSD                |
| 에러 메시지  | 불친절함         | 친절하고 명확함           |
| 디버거     | `gdb`        | `lldb`             |
| 플랫폼     | Linux 중심     | macOS, Android 등   |


