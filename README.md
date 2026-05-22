# rsod-web-platform
农业病虫害智能识别系统

## 数据集准备

本项目使用 [PlantVillage](https://modelscope.cn/datasets/OmniData/PlantVillage) 数据集，共 38 类植物病害图片，约 54,000 张。

> 数据集体积较大，不纳入版本管理，需本地手动下载后运行预处理脚本生成。

### 1. 下载数据集

前往魔搭社区下载数据集：

**链接：** https://modelscope.cn/datasets/OmniData/PlantVillage

点击页面右上角 **"下载数据集"**，选择 `Plant_leaf_diseases_dataset_without_augmentation.zip` 下载。

### 2. 放置数据集

将下载的 zip 文件放到以下路径（路径不存在时手动创建）：

```
D:\datasets\PlantVillage\raw\Plant_leaf_diseases_dataset_without_augmentation.zip
```

### 3. 运行预处理脚本

在项目根目录执行：

```bash
python scripts/prepare_dataset.py
```

脚本会自动完成以下工作：

- 解压原始数据集
- 按 **8:1:1** 划分 train / val / test
- 对 train 集中样本不足 1000 张的类别进行数据增强（翻转、旋转、亮度、对比度等）补齐至 1000 张
- 统一缩放图片至 224×224
- 生成 `dataset/dataset.yaml`（供 YOLO11 训练直接使用）

处理完成后目录结构如下：

```
dataset/
├── train/          # 训练集（含增强，每类 ≥ 1000 张）
├── val/            # 验证集
├── test/           # 测试集
├── dataset.yaml    # YOLO11 配置文件
└── dataset_stats.json  # 各类别数量统计
```

预计耗时：5 ~ 15 分钟（视磁盘速度而定）。
