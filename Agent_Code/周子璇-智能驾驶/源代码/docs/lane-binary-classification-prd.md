# Product Requirements Document: 车道线二分类感知

**Version**: 1.0  
**Date**: 2026-05-15  
**Author**: 周子璇

---

## Executive Summary

本项目面向自动驾驶基础感知场景，实现一个“车道内 / 车道外”二分类模型。系统不追求精确拟合车道线形状，而是基于车载前视图像中的车辆前方 ROI，快速判断当前区域是否属于可行驶车道区域。

项目将使用 TuSimple 开源车道线数据集，通过车道线坐标自动构造二分类样本，采用 PyTorch + ResNet18 作为主模型，并在 MVP 中包含图像增强、TensorBoard 训练记录、ONNX 导出和 ONNX Runtime 推理能力。最终交付源代码压缩包、PPT 设计文档和简短实验报告。

---

## Problem Statement

**Current Situation**: 传统车道线检测通常需要输出精确线形、车道边界或分割结果，实现复杂、调试成本较高；但在部分自动驾驶感知验证场景中，只需要快速判断车辆当前前方区域是否处于车道内。

**Proposed Solution**: 将车道感知问题简化为图像二分类任务。系统读取 TuSimple 前视图像及车道线坐标，裁剪车辆前方 ROI，自动生成“车道内 / 车道外”标签，训练 ResNet18 分类模型并提供 PyTorch 与 ONNX Runtime 两种推理方式。

**Business / Learning Impact**: 该项目可用较低复杂度验证自动驾驶感知中的基础决策能力，适合作为课程实验或原型系统，能够展示数据预处理、深度学习训练、模型评估、可视化和模型部署的完整流程。

---

## Success Metrics

**Primary KPIs:**
- **验证集 Accuracy**: ≥ 85%，通过保留验证集评估得到。
- **验证集 F1-score**: ≥ 0.80，避免仅依赖准确率导致类别不平衡误判。
- **ONNX 推理一致性**: PyTorch 与 ONNX Runtime 对同一批验证样本的预测类别一致率 ≥ 99%。
- **可复现实验**: 在说明的 Python 版本和依赖环境下，可完成数据准备、训练、评估、ONNX 导出与推理。

**Validation**: 在实验报告中记录训练/验证曲线、混淆矩阵、分类指标、预测样例和 ONNX Runtime 推理截图或日志。

---

## User Stories & Acceptance Criteria

### Story 1: 数据集准备与标签构造

**As a** 课程项目开发者  
**I want to** 从 TuSimple 数据集中自动生成车道内 / 车道外二分类样本  
**So that** 我可以训练分类模型而不需要手动标注所有图片。

**Acceptance Criteria:**
- [ ] 系统能读取 TuSimple 图像路径和车道线标注 JSON。
- [ ] 系统能根据车道线坐标判断 ROI 是否位于主车道区域内。
- [ ] 系统能生成 `train/val/test` 数据划分。
- [ ] 系统能输出 inside/outside 类别样本数量统计。
- [ ] 当图像缺少有效车道线标注时，系统应跳过样本并记录数量。

### Story 2: 模型训练

**As a** 课程项目开发者  
**I want to** 使用 ResNet18 训练车道内 / 车道外分类模型  
**So that** 我可以获得可用于推理和评估的模型权重。

**Acceptance Criteria:**
- [ ] 模型输入为裁剪后的 RGB ROI，默认 resize 到 `224 x 224`。
- [ ] 模型输出为两个类别 logits：`inside` 和 `outside`。
- [ ] 训练过程记录 train loss、val loss、train accuracy、val accuracy。
- [ ] 最佳模型按验证集 F1-score 或 accuracy 保存到 `checkpoints/best_model.pth`。
- [ ] 训练过程写入 TensorBoard 日志目录 `runs/`。

### Story 3: 模型评估与实验结果

**As a** 项目评审者  
**I want to** 查看模型在验证集上的分类指标和可视化结果  
**So that** 我可以判断模型是否真正具备基础感知能力。

**Acceptance Criteria:**
- [ ] 评估脚本输出 Accuracy、Precision、Recall、F1-score。
- [ ] 评估脚本生成混淆矩阵图片。
- [ ] 系统保存若干正确预测和错误预测样例。
- [ ] 实验报告包含关键指标、训练曲线和结果分析。

### Story 4: 单张图片推理

**As a** 课程项目开发者  
**I want to** 输入一张前视图像并得到车道内 / 车道外预测  
**So that** 我可以展示模型在新样本上的基础决策能力。

**Acceptance Criteria:**
- [ ] 推理脚本支持传入单张图片路径。
- [ ] 推理脚本自动裁剪与训练一致的 ROI。
- [ ] 推理输出类别、置信度和可选可视化图片。
- [ ] 无法读取图片时，脚本给出明确错误信息。

### Story 5: ONNX 导出与 ONNX Runtime 推理

**As a** 课程项目开发者  
**I want to** 将模型导出为 ONNX 并使用 ONNX Runtime 推理  
**So that** 我可以展示模型部署与跨框架推理能力。

**Acceptance Criteria:**
- [ ] 导出脚本生成 `outputs/model.onnx`。
- [ ] ONNX 模型通过 `onnx.checker` 校验。
- [ ] ONNX Runtime 推理脚本输出类别和置信度。
- [ ] 同一测试样本上，PyTorch 和 ONNX Runtime 预测类别基本一致。

---

## Functional Requirements

### Core Feature 1: TuSimple 数据解析
- **Description**: 读取 TuSimple JSON 标注文件，获取图像路径、车道线横坐标列表和对应 y 坐标列表。
- **User Flow**:
  1. 用户下载并解压 TuSimple 数据集。
  2. 用户配置数据集根目录。
  3. 运行数据准备脚本。
  4. 系统生成二分类样本清单或裁剪后的图片目录。
- **Edge Cases**: 无效坐标、缺失图像、车道线数量不足、JSON 格式异常。
- **Error Handling**: 跳过不可用样本并在日志中统计，不中断整体数据生成流程。

### Core Feature 2: ROI 裁剪与标签生成
- **Description**: 从前视图像下半部分裁剪车辆前方 ROI，并根据 ROI 中心点是否位于主车道左右边界之间生成标签。
- **Default ROI Strategy**:
  - 使用图像下方区域作为车辆前方 ROI，例如 `y = 0.55H ~ 0.95H`，`x = 0.25W ~ 0.75W`。
  - 将 ROI resize 到 `224 x 224`。
- **Default Label Rule**:
  - 选择最靠近车辆中心线的左右两条有效车道线作为主车道边界。
  - 在 ROI 中心点对应的 y 坐标处插值得到左右边界 x 坐标。
  - 若 ROI 中心 x 位于左右边界之间，则标记为 `inside`，否则标记为 `outside`。
- **Edge Cases**: 如果无法找到左右边界，则跳过该样本或作为低置信样本不进入训练集。
- **Error Handling**: 输出 skipped count，确保训练数据来源清晰。

### Core Feature 3: 图像增强
- **Description**: 在训练阶段对 ROI 图像做增强以提高泛化能力。
- **Required Augmentations**:
  - 随机亮度 / 对比度变化。
  - 随机水平翻转。
  - 轻微颜色扰动。
- **Constraints**:
  - 不使用垂直翻转，因为道路图像上下语义不可逆。
  - 验证集只做 resize、normalize，不做随机增强。

### Core Feature 4: ResNet18 二分类训练
- **Description**: 使用 torchvision ResNet18 作为 backbone，将最后全连接层改为二分类输出。
- **User Flow**:
  1. 用户运行训练脚本并指定数据目录。
  2. 系统加载数据、模型和训练配置。
  3. 系统训练模型并在验证集上选择最佳权重。
  4. 系统保存模型、日志和训练曲线。
- **Edge Cases**: GPU 不可用时自动使用 CPU；类别不平衡时支持 class weight 或 weighted sampler。
- **Error Handling**: 如果数据目录为空或类别不足，训练前直接报错并说明缺失内容。

### Core Feature 5: 评估与可视化
- **Description**: 使用保留验证集评估模型，并生成实验报告需要的关键结果。
- **Outputs**:
  - `outputs/metrics.json`
  - `outputs/confusion_matrix.png`
  - `outputs/predictions/` 样例图
- **Edge Cases**: 验证集为空、只有单类别样本、模型权重不存在。
- **Error Handling**: 在评估前检查输入条件，失败时输出明确错误。

### Core Feature 6: ONNX 导出与推理
- **Description**: 将训练完成的 PyTorch 模型导出为 ONNX，并通过 ONNX Runtime 对图片进行推理。
- **Outputs**:
  - `outputs/model.onnx`
  - ONNX Runtime 推理日志
- **Edge Cases**: ONNX 依赖未安装、模型输入维度不匹配、导出失败。
- **Error Handling**: 输出安装提示和失败原因。

### Out of Scope
- 不要求输出精确车道线曲线。
- 不要求做语义分割、实例分割或 BEV 车道建模。
- 不要求实时视频流推理。
- 不要求接入真实车辆或 ROS 系统。
- 不要求多类别道路场景分类。

---

## Technical Constraints

### Performance
- 单张 ROI 推理时间：GPU 环境下目标 `< 20ms`，CPU 环境下目标 `< 100ms`。
- 训练输入尺寸默认 `224 x 224`。
- 支持小规模课程实验数据，建议训练集不少于每类 500 张样本。

### Security & Compliance
- 数据集仅使用公开开源数据或课程允许数据。
- 不在代码中硬编码本地绝对路径、账号、密钥或私人数据。
- 提交压缩包不包含大型原始数据集，仅包含代码、配置、少量示例和说明。

### Integration
- **TuSimple Dataset**: 作为主要数据来源，依赖其图像和 JSON 车道线标注。
- **TensorBoard**: 记录训练过程，用于展示 loss / accuracy 曲线。
- **ONNX / ONNX Runtime**: 用于模型导出与部署推理验证。

### Technology Stack
- Python 3.10+
- PyTorch 2.x
- torchvision
- OpenCV 或 Pillow
- NumPy
- scikit-learn
- matplotlib
- tensorboard
- onnx
- onnxruntime

---

## MVP Scope & Phasing

### Phase 1: MVP Required for Initial Launch
- TuSimple 数据解析与二分类标签生成。
- ROI 裁剪与数据集划分。
- ResNet18 二分类训练。
- 图像增强。
- TensorBoard 训练记录。
- 验证集评估与混淆矩阵。
- 单张图片 PyTorch 推理。
- ONNX 导出与 ONNX Runtime 推理。
- 源代码、PPT、简短实验报告。

**MVP Definition**: 用户可以从 TuSimple 数据集生成训练数据，训练 ResNet18 二分类模型，在验证集上得到可量化结果，并通过 PyTorch 与 ONNX Runtime 对新图片输出“车道内 / 车道外”判断。

### Phase 2: Enhancements
- 增加简单 CNN baseline，与 ResNet18 对比。
- 支持更多数据集，如 CULane 或 BDD100K。
- 增加 Grad-CAM 可解释性可视化。
- 增加批量推理和结果 HTML 报告。

### Future Considerations
- 支持视频流逐帧推理。
- 支持车道偏离风险等级，而不只是二分类。
- 使用分割 mask 生成更稳定的车道区域标签。

---

## Technical Solution

### 1. Recommended Architecture

```text
TuSimple Raw Dataset
        |
        v
prepare_dataset.py
  - parse JSON labels
  - select ROI
  - infer inside/outside label
  - split train/val/test
        |
        v
data/processed/
  train/inside, train/outside
  val/inside, val/outside
  test/inside, test/outside
        |
        v
train.py -> checkpoints/best_model.pth + runs/
        |
        +-> evaluate.py -> metrics.json + confusion_matrix.png
        |
        +-> infer.py -> PyTorch single-image prediction
        |
        +-> export_onnx.py -> outputs/model.onnx
                  |
                  v
              infer_onnx.py
```

### 2. Suggested Repository Structure

```text
Lane_classification/
  configs/
    default.yaml
  data/
    processed/
  docs/
    lane-binary-classification-prd.md
  src/
    __init__.py
    dataset.py
    model.py
    transforms.py
    train.py
    evaluate.py
    infer.py
    prepare_tusimple.py
    export_onnx.py
    infer_onnx.py
    utils.py
  checkpoints/
  outputs/
  runs/
  requirements.txt
```

### 3. Data Preparation Design

**Input**: TuSimple JSON lines annotation file and image root directory.

**Processing Steps**:
1. Read each annotation record.
2. Load `raw_file`, `lanes`, and `h_samples`.
3. Filter invalid x coordinates, commonly `-2` in TuSimple.
4. At a selected ROI center y position, interpolate lane x coordinates.
5. Identify left and right lane boundaries closest to image center.
6. Crop ROI from the original image.
7. Assign label:
   - `inside`: ROI center lies between left and right lane boundary.
   - `outside`: ROI center lies outside the main lane region.
8. Save cropped image or save metadata CSV.
9. Split into train / val / test, for example 70% / 15% / 15%.

**Class Balance Strategy**:
- Track inside/outside counts.
- If one class is much larger, downsample majority class or use weighted sampler.

### 4. Model Design

**Main Model**: ResNet18.

```text
Input: 3 x 224 x 224 ROI image
Backbone: torchvision.models.resnet18
Classifier: Linear(in_features, 2)
Output: logits for [outside, inside]
Loss: CrossEntropyLoss
Optimizer: Adam or AdamW
Scheduler: StepLR or CosineAnnealingLR
```

**Recommended Training Parameters**:
- Epochs: 15-30
- Batch size: 32
- Learning rate: 1e-4 for pretrained ResNet18, 1e-3 if training classifier head first
- Weight decay: 1e-4
- Early stopping: patience 5 based on validation F1-score

### 5. Transform Design

**Train Transform**:
```text
Resize(224, 224)
RandomHorizontalFlip(p=0.5)
ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2)
ToTensor()
Normalize(ImageNet mean/std)
```

**Validation/Test Transform**:
```text
Resize(224, 224)
ToTensor()
Normalize(ImageNet mean/std)
```

### 6. Evaluation Design

Evaluation script should compute:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix
- Per-class support

It should also save:
- Metrics JSON
- Confusion matrix image
- Sample prediction images with predicted label and confidence

### 7. ONNX Deployment Design

**Export Requirements**:
- Input name: `input`
- Output name: `logits`
- Dynamic batch axis supported
- Opset version: 12 or higher

**Verification Steps**:
1. Load PyTorch checkpoint.
2. Export ONNX with dummy input `1 x 3 x 224 x 224`.
3. Validate using `onnx.checker.check_model`.
4. Run ONNX Runtime on a small image batch.
5. Compare predicted labels against PyTorch outputs.

### 8. Suggested CLI Commands

Windows PowerShell 环境建议先设置源码路径：

```powershell
$env:PYTHONPATH='src'
```

快速验证完整工程流程：

```powershell
python -m lane_classification.run_pipeline --workspace outputs/smoke --smoke --skip-onnx
```

模块化运行方式如下：

```powershell
python -m lane_classification.prepare_tusimple path/to/label_data.json --image-root path/to/tusimple --output-root data/processed --split train --mode dynamic
python -m lane_classification.train --train-dir data/processed/train --val-dir data/processed/val --checkpoint checkpoints/best_model.pth --epochs 20 --batch-size 32
python -m lane_classification.evaluate --data-dir data/processed/val --checkpoint checkpoints/best_model.pth --metrics-json outputs/metrics.json
python -m lane_classification.infer --image path/to/image.jpg --checkpoint checkpoints/best_model.pth
python -m lane_classification.export_onnx --checkpoint checkpoints/best_model.pth --output outputs/model.onnx
python -m lane_classification.infer_onnx --image path/to/image.jpg --model outputs/model.onnx
```

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| TuSimple 原始标注不能直接对应二分类标签 | Medium | High | 在 PRD 中明确 ROI 中心点和主车道边界规则，并保存跳过样本统计。 |
| inside/outside 类别不平衡 | High | Medium | 数据生成阶段统计类别数量，训练阶段使用 downsample、class weight 或 weighted sampler。 |
| 模型只学习道路纹理而非车道区域语义 | Medium | Medium | 使用图像增强、错误样例分析和跨场景测试样本检查泛化。 |
| ONNX 导出与 PyTorch 推理不一致 | Low | Medium | 固定 eval 模式，统一预处理流程，导出后做一致性测试。 |
| 数据集过大导致提交包臃肿 | Medium | Medium | 不提交原始数据集，只提交代码、配置、少量示例和数据准备说明。 |

---

## Dependencies & Blockers

**Dependencies:**
- TuSimple 开源车道线数据集：需要用户自行下载到本地。
- Python 深度学习环境：需要安装 PyTorch、torchvision、OpenCV/Pillow 等依赖。
- 可选 GPU：提升训练速度，但不是硬性要求。

**Known Blockers:**
- 如果无法获取 TuSimple 数据集，则需要切换到人工小样本目录或其他开源数据集。
- 如果本地环境无法安装 PyTorch 或 ONNX Runtime，则无法完成完整 MVP 验收。

---

## Deliverables

### Source Code Package
- 数据准备脚本。
- 模型定义脚本。
- 训练脚本。
- 评估脚本。
- PyTorch 推理脚本。
- ONNX 导出与 ONNX Runtime 推理脚本。
- 依赖文件与运行说明。

### PPT Design Document
Recommended sections:
1. 项目背景与任务目标。
2. 数据集来源与样本构造。
3. ROI 裁剪与标签规则。
4. 模型结构。
5. 训练配置。
6. TensorBoard 训练曲线。
7. 验证集结果与混淆矩阵。
8. ONNX Runtime 推理展示。
9. 总结与不足。

### Short Experiment Report
Recommended sections:
1. 实验目的。
2. 数据集与预处理。
3. 方法设计。
4. 模型结构与训练参数。
5. 实验结果。
6. 错误样例分析。
7. 总结。

---

## Appendix

### Glossary
- **ROI**: Region of Interest，图像中用于模型输入的局部区域。
- **Inside**: 当前 ROI 中心位于主车道左右边界之间。
- **Outside**: 当前 ROI 中心不在主车道左右边界之间。
- **TuSimple**: 常用开源车道线检测数据集，包含前视图像与车道线点标注。
- **ONNX**: Open Neural Network Exchange，用于跨框架模型部署的开放格式。

### References
- TuSimple Lane Detection Dataset
- PyTorch / torchvision ResNet18
- TensorBoard
- ONNX Runtime

---

*This PRD was created through interactive requirements gathering with quality scoring to ensure comprehensive coverage of business, functional, UX, and technical dimensions.*
