import torch
import torch.nn as nn
import geoopt

# 中文注释: 定义洛伦兹线性层
class LorentzLinear(nn.Module):
    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.manifold = geoopt.manifolds.Lorentz()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features)) if bias else None

    def forward(self, x):
        # 将权重和输入映射到洛伦兹流形上
        x = self.manifold.expmap0(x)
        w = self.manifold.expmap0(self.weight)
        out = self.manifold.inner(None, x.unsqueeze(1), w.unsqueeze(0)).squeeze(-1)
        if self.bias is not None:
            out = out + self.bias
        return out


# 中文注释: 基于洛伦兹流形的图卷积层
class LorentzGCNLayer(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.lin = LorentzLinear(in_features, out_features)

    def forward(self, x, adj):
        # 简单的图卷积传播规则
        support = self.lin(x)
        out = torch.matmul(adj, support)
        return out


class LorentzGCN(nn.Module):
    def __init__(self, num_features, hidden_dim, num_classes):
        super().__init__()
        self.layer1 = LorentzGCNLayer(num_features, hidden_dim)
        self.act = nn.ReLU()
        self.layer2 = LorentzGCNLayer(hidden_dim, num_classes)

    def forward(self, x, adj):
        x = self.layer1(x, adj)
        x = self.act(x)
        x = self.layer2(x, adj)
        return x
