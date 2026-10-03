# Deconvnet (Zeiler & Fergus, 2014) 샘플 구현
# 실행에 필요한 패키지: pip install torch
#
# 핵심 아이디어
#   1) forward 시 Conv-ReLU-Pool을 거치며 MaxPool의 위치 정보(switch)를 저장해둔다.
#   2) 특정 feature map의 특정 채널(활성값)만 남기고 나머지는 0으로 지운다.
#   3) 역방향으로 Unpool(switch 사용) -> ReLU -> Deconv(같은 필터의 전치)를 거치며
#      해당 활성이 입력 이미지의 어떤 픽셀 패턴에 반응했는지 재구성한다.
#
# Deconv는 별도의 학습 파라미터를 갖지 않고, forward에서 쓰인 conv weight를
# 그대로 전치해서 사용한다 (논문에서 말하는 "using transposed versions of the same filters").

import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvNet(nn.Module):
    """시각화 대상이 되는 아주 단순한 2단 Conv-ReLU-Pool 네트워크"""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2, return_indices=True)

        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2, return_indices=True)

    def forward(self, x):
        switches = {}
        sizes = {}

        x = F.relu(self.conv1(x))
        sizes["pool1_in"] = x.size()
        x, idx1 = self.pool1(x)
        switches["pool1"] = idx1

        x = F.relu(self.conv2(x))
        sizes["pool2_in"] = x.size()
        x, idx2 = self.pool2(x)
        switches["pool2"] = idx2

        return x, switches, sizes


class DeconvNet(nn.Module):
    """ConvNet과 대칭을 이루며, 같은 conv weight를 전치해서 재사용하는 deconv 네트워크"""

    def __init__(self, convnet: ConvNet):
        super().__init__()
        self.convnet = convnet
        self.unpool2 = nn.MaxUnpool2d(kernel_size=2, stride=2)
        self.unpool1 = nn.MaxUnpool2d(kernel_size=2, stride=2)

    def forward(self, feature, switches, sizes):
        x = self.unpool2(feature, switches["pool2"], output_size=sizes["pool2_in"])
        x = F.relu(x)
        x = F.conv_transpose2d(x, self.convnet.conv2.weight, padding=1)

        x = self.unpool1(x, switches["pool1"], output_size=sizes["pool1_in"])
        x = F.relu(x)
        x = F.conv_transpose2d(x, self.convnet.conv1.weight, padding=1)

        return x


def isolate_strongest_activation(feature_map: torch.Tensor) -> torch.Tensor:
    """feature map에서 가장 강하게 반응한 채널의 가장 강한 위치 하나만 남기고 나머지는 0으로 만든다."""
    isolated = torch.zeros_like(feature_map)

    batch, channels, h, w = feature_map.shape
    for b in range(batch):
        flat_idx = torch.argmax(feature_map[b])
        c, y, x = torch.unravel_index(flat_idx, (channels, h, w))
        isolated[b, c, y, x] = feature_map[b, c, y, x]

    return isolated


if __name__ == "__main__":
    torch.manual_seed(0)

    convnet = ConvNet()
    deconvnet = DeconvNet(convnet)

    image = torch.randn(1, 3, 32, 32)  # 임의의 입력 이미지 (배치 1, RGB, 32x32)

    feature, switches, sizes = convnet(image)
    print("pool2 output feature map shape:", feature.shape)

    # 가장 강하게 활성화된 뉴런 하나만 골라 나머지는 0으로 지운다
    isolated_feature = isolate_strongest_activation(feature)

    # 그 뉴런이 입력 공간에서 어떤 패턴에 반응했는지 재구성
    reconstruction = deconvnet(isolated_feature, switches, sizes)
    print("reconstructed input pattern shape:", reconstruction.shape)
    print("nonzero pixels in reconstruction:", torch.count_nonzero(reconstruction).item())
