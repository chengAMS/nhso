# Lorentz GCNN 示例

本项目演示如何在洛伦兹流形上实现图卷积神经网络，并结合持久同调特征进行增强。

## 依赖安装
```
pip install torch geoopt giotto-tda networkx scikit-learn matplotlib
```

## 运行训练
```
python train.py
```
训练完成后将在当前目录生成`prediction.png`，可视化节点预测结果。
