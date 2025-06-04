import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import networkx as nx
import numpy as np
from gtda.homology import VietorisRipsPersistence
from lorentz_gcnn.model import LorentzGCN

# 中文注释: 生成一个简单的合成图数据集
G = nx.karate_club_graph()
features = np.eye(G.number_of_nodes())
adj = nx.to_numpy_array(G)
labels = np.array([G.nodes[i]['club'] == 'Mr. Hi' for i in range(G.number_of_nodes())], dtype=int)

# 中文注释: 计算持久同调特征
vr = VietorisRipsPersistence(homology_dimensions=[0,1])
pairs = features.reshape(features.shape[0], -1, 1)
ph_features = vr.fit_transform(pairs)
ph_features = ph_features.reshape(ph_features.shape[0], -1)
ph_features = StandardScaler().fit_transform(ph_features)
# 中文注释: 划分训练和测试集
idx = np.arange(len(labels))
train_idx, test_idx = train_test_split(idx, test_size=0.3, random_state=42)

x = torch.tensor(np.concatenate([features, ph_features], axis=1), dtype=torch.float)
adj = torch.tensor(adj, dtype=torch.float)
labels = torch.tensor(labels, dtype=torch.long)

model = LorentzGCN(x.shape[1], 16, 2)
optimizer = optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.CrossEntropyLoss()

# 训练
for epoch in range(100):
    model.train()
    logits = model(x, adj)
    loss = loss_fn(logits[train_idx], labels[train_idx])
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 20 == 0:
        print(f"Epoch {epoch+1}, loss: {loss.item():.4f}")

# 测试
model.eval()
with torch.no_grad():
    preds = model(x, adj).argmax(dim=1)
    acc = accuracy_score(labels[test_idx].numpy(), preds[test_idx].numpy())
print("Test accuracy:", acc)

# 可视化
pos = nx.spring_layout(G)
color_map = ['red' if p == 1 else 'blue' for p in preds.numpy()]
plt.figure(figsize=(6,4))
nx.draw(G, pos, node_color=color_map, with_labels=True)
plt.title('Prediction Visualization')
plt.savefig('prediction.png')
plt.close()
