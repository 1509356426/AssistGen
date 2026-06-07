# 车道线二分类感知系统

本项目基于 TuSimple Lane Detection 数据集，将原始车道线标注转换为动态 ROI 的 inside / outside 二分类任务，并完成模型训练、评估、推理、ONNX 导出和结果可视化。

## 项目内容

- `src/lane_classification/`：核心源码，包括数据处理、模型、训练、评估、推理和一键 smoke pipeline。
- `tests/`：自动化测试，用于验证数据、模型、训练、评估、推理和 ONNX 流程。
- `docs/`：实验报告、PPT 内容、实际 PPT 文件、结果可视化 PDF 和图表资源。
- `outputs/`：最终实验指标、ONNX 模型和错误样例分析结果。
- `checkpoints/`：训练得到的 PyTorch 模型权重。

## 环境安装

本项目测试环境如下：

| 项目 | 版本 |
|---|---|
| Python | 3.12.9 |
| PyTorch | 2.11.0+cu128 |
| torchvision | 0.26.0+cu128 |
| CUDA | 12.8 |
| GPU | NVIDIA GeForce RTX 5060 |
| numpy | 2.4.4 |
| Pillow | 12.2.0 |
| tensorboard | 2.20.0 |
| onnx | 1.21.0 |
| onnxruntime | 1.21.0 |
| pytest | 9.0.3 |

安装依赖：

```powershell
pip install -r requirements.txt
```

`requirements.txt` 中列出了项目运行和测试需要的主要依赖，包括 PyTorch、torchvision、Pillow、numpy、TensorBoard、ONNX、ONNX Runtime 和 pytest 等。完整训练使用 CUDA 环境完成；如果只是检查项目流程，CPU 环境也可以运行一键快速验证命令。

## 一键快速验证

该命令用于快速验证项目端到端流程，不会重新训练完整 TuSimple 30 epoch 模型：

```powershell
$env:PYTHONPATH='src'
python -m lane_classification.run_pipeline --workspace outputs/smoke --smoke --skip-onnx
```

如果 ONNX 和 ONNX Runtime 环境正常，可以运行完整 smoke 部署验证：

```powershell
$env:PYTHONPATH='src'
python -m lane_classification.run_pipeline --workspace outputs/smoke --smoke
```

运行成功后会生成：

```text
outputs/smoke/metrics.json
outputs/smoke/summary.json
outputs/smoke/checkpoints/lane.pt
```

## 自动化测试

```powershell
$env:PYTHONPATH='src'
pytest -q
```

当前验证结果：

```text
48 passed, 6 warnings
```

## 最终实验结果

完整 TuSimple 动态 ROI 30 epoch CUDA 实验结果位于：

```text
outputs/tusimple_dynamic_cuda_30ep_metrics.json
```

核心指标：

| 指标 | 数值 |
|---|---:|
| Accuracy | 99.80% |
| Precision | 99.82% |
| Recall | 99.82% |
| F1-score | 99.82% |
| 验证集样本数 | 4961 |
| 总错误数 | 10 |

## 提交材料位置

| 文件 | 说明 |
|---|---|
| `docs/lane-binary-classification-experiment-report.md` | 实验报告正文 |
| `docs/lane-binary-classification-presentation.pptx` | 答辩 PPT |
| `docs/lane-binary-classification-visualization.pdf` | 结果可视化 PDF |
| `outputs/tusimple_dynamic_cuda_30ep_metrics.json` | 最终验证集指标 |
| `outputs/error_analysis/` | 错误样例分析结果 |
| `checkpoints/tusimple_dynamic_resnet18_cuda_30ep.pth` | 最终 PyTorch 模型权重 |
| `outputs/tusimple_dynamic_resnet18_cuda_30ep.onnx` | 最终 ONNX 模型 |
