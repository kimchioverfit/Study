
import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()

        # 1. Feature Extractor
        # 입력 이미지를 feature map으로 바꾸는 부분
        self.features = nn.Sequential(
            # Input: [B, 3, 224, 224]
            nn.Conv2d(
                in_channels=3,
                out_channels=32,
                kernel_size=3,
                stride=1,
                padding=1
            ),
            nn.ReLU(),

            # [B, 32, 224, 224] -> [B, 32, 112, 112]
            nn.MaxPool2d(kernel_size=2, stride=2),

            # [B, 32, 112, 112] -> [B, 64, 112, 112]
            nn.Conv2d(
                in_channels=32,
                out_channels=64,
                kernel_size=3,
                stride=1,
                padding=1
            ),
            nn.ReLU(),

            # [B, 64, 112, 112] -> [B, 64, 56, 56]
            nn.MaxPool2d(kernel_size=2, stride=2),

            # [B, 64, 56, 56] -> [B, 128, 56, 56]
            nn.Conv2d(
                in_channels=64,
                out_channels=128,
                kernel_size=3,
                stride=1,
                padding=1
            ),
            nn.ReLU(),

            # [B, 128, 56, 56] -> [B, 128, 28, 28]
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # 2. Classifier
        # feature map을 최종 class score로 바꾸는 부분
        self.classifier = nn.Sequential(
            # [B, 128, 28, 28] -> [B, 128, 1, 1]
            nn.AdaptiveAvgPool2d((1, 1)),

            # [B, 128, 1, 1] -> [B, 128]
            nn.Flatten(),

            # [B, 128] -> [B, 2]
            # 예: 0 = OK, 1 = NG
            nn.Linear(128, 2),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


model = SimpleCNN()

x = torch.randn(8, 3, 224, 224)  # batch 8장, RGB, 224x224
out = model(x)

print(out.shape)