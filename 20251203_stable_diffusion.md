# Stable diffusion 

SD3 Medium, Diffuser사용 Version

전체 프로세스

```powershell
pip install "tokenizers>=0.19,<0.21" --only-binary=:all:
pip install -U "huggingface_hub[cli]" diffusers transformers accelerate safetensors sentencepiece

```

구버전 tokenizers가 Rust 빌드를 시도하며 설치 실패 → 필연적 오류 발생하므로 

--only-binary=:all: 옵션 이용 

```
hf auth login
hf auth logout
```
이런거 이용해서 huggingface 로그인 해줘야하고, Token설정 꼭해줘야함.

Token 설정 옵션에서 해당 Repository 찾아서 추가하는거 잊지말자 

