
```python
import numpy as np
from numba import cuda, float32

# 2D Convolution CUDA 커널
@cuda.jit
def conv2d_kernel(img, kernel, output):
    i, j = cuda.grid(2)
    kH, kW = kernel.shape
    H, W = img.shape

    # 유효한 범위 내에서만 계산 (valid padding)
    if i < H - kH + 1 and j < W - kW + 1:
        val = 0.0
        for ki in range(kH):
            for kj in range(kW):
                val += img[i + ki, j + kj] * kernel[ki, kj]
        output[i, j] = val

# 입력 이미지와 필터
image = np.random.rand(64, 64).astype(np.float32)
kernel = np.array([[1, 0, -1],
                   [1, 0, -1],
                   [1, 0, -1]], dtype=np.float32)  # Sobel-like 필터

# 출력 배열 (valid padding)
out_shape = (image.shape[0] - kernel.shape[0] + 1,
             image.shape[1] - kernel.shape[1] + 1)
output = np.zeros(out_shape, dtype=np.float32)

# GPU 메모리로 복사
d_img = cuda.to_device(image)
d_kernel = cuda.to_device(kernel)
d_output = cuda.device_array(out_shape, dtype=np.float32)

# 커널 실행 구성
threadsperblock = (16, 16)
blockspergrid_x = (out_shape[0] + threadsperblock[0] - 1) // threadsperblock[0]
blockspergrid_y = (out_shape[1] + threadsperblock[1] - 1) // threadsperblock[1]
blockspergrid = (blockspergrid_x, blockspergrid_y)

# CUDA 커널 실행
conv2d_kernel[blockspergrid, threadsperblock](d_img, d_kernel, d_output)

# 결과 복사
result = d_output.copy_to_host()

# 결과 확인
print("Convolution 결과 (일부):")
print(result[:5, :5])
```

@cuda.jit은 이 함수가 CUDA 커널임을 알려준다.

