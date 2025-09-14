# Kernel module

커널에 동적으로 기능 추가/삭제 가능한 플로그인 개념.

커널 전체를 Compile하지 않아도 되어서 좋음.

### 커널도 Compile이 필요한가...?

Yes. 커널도 결국 SW이므로, Compile이 필요하다.

Build 되면 vmlinuz 같은 Kernel bin 파일이 생성되고,

부팅 시 메모리에 올라가서 OS의 핵심 역할을 수행한다.

### Kernel module 방법

Kernel의 일부 기능은 외부파일 (.ko)같은걸로 분리해서

동적으로 로드/언로드 해서 사용하면 된다. 

(insmod/rmmod) - 상세 내용은 리눅스 검색 참조