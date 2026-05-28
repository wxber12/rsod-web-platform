<template>
  <div class="detection-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="breadcrumb">
        <span>工作台</span>
        <span class="separator">›</span>
        <span class="active">智能检测</span>
      </div>
      <h1 class="page-title">上传作物影像，立即识别病虫害</h1>
      <p class="page-subtitle">
        支持苹果疮痂病 / 玉米锈病 / 棉铃虫 / 番茄早疫病 等多目标检测
      </p>
    </div>

    <!-- 模型选择器 -->
    <div class="model-selector">
      <el-select v-model="selectedModel" style="width: 200px" placeholder="选择检测模型">
        <el-option
          v-for="model in availableModels"
          :key="model.name"
          :label="model.name"
          :value="model.name"
        />
      </el-select>
    </div>

    <!-- 功能选项卡 -->
    <div class="function-tabs">
      <div
        v-for="tab in functionTabs"
        :key="tab.key"
        class="function-tab"
        :class="{ active: activeTab === tab.key }"
        :data-key="tab.key"
        @click="handleTabClick(tab.key)"
      >
        <input
          v-if="tab.key !== 'camera'"
          type="file"
          :accept="tab.accept"
          :multiple="tab.multiple"
          :webkitdirectory="tab.webkitdirectory"
          :directory="tab.webkitdirectory"
          class="file-input"
          @change="handleFileChange($event, tab.key)"
          @click.stop
          ref="fileInputs"
        />
        <el-icon :size="18" class="tab-icon"><component :is="tab.icon" /></el-icon>
        <span class="tab-text">{{ tab.name }}</span>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧检测结果区域 -->
      <div class="left-panel">
        <div class="panel-header">
          <span class="panel-title">检测预览</span>
          <el-tag v-if="isDetecting" type="warning" effect="light" class="result-tag">
            <el-icon class="el-icon--left is-loading"><Loading /></el-icon>
            正在检测...
          </el-tag>
          <el-tag v-else-if="detectionResult" type="success" effect="light" class="result-tag">
            <el-icon class="el-icon--left"><Check /></el-icon>
            检测完成 (耗时: {{ detectionResult.detection_time }}s)
          </el-tag>
        </div>

        <!-- 工具栏 -->
        <div class="toolbar">
          <el-button
            :class="{ active: compareMode === 'side' }"
            size="small"
            @click="compareMode = 'side'"
          >
            <el-icon><Minus /></el-icon>
            并排对比
          </el-button>
          <el-button
            :class="{ active: compareMode === 'grid' }"
            size="small"
            @click="compareMode = 'grid'"
          >
            <el-icon><Grid /></el-icon>
            栅格对比
          </el-button>
        </div>

        <!-- 摄像头检测区域 -->
        <div v-if="activeTab === 'camera'" class="camera-section">
          <CameraDetection :model-name="selectedModel" @detected="handleCameraDetected" />
        </div>

        <!-- 图片对比区域 -->
        <div v-else class="image-compare">
          <div class="image-card">
            <video
              v-if="originalVideo"
              :src="originalVideo"
              controls
              class="compare-image"
            />
            <img
              v-else-if="originalImage"
              :src="originalImage"
              alt="原始图片"
              class="compare-image"
            />
            <div v-else class="image-placeholder">请上传作物图片/视频</div>
            <div class="image-label">原始{{ activeTab === 'video' ? '视频' : '图片' }}</div>
          </div>
          <div class="image-card" v-loading="isDetecting" element-loading-text="AI正在疯狂识别中...">
            <video
              v-if="resultVideo"
              :src="resultVideo"
              controls
              class="compare-image"
            />
            <img
              v-else-if="resultImage"
              :src="resultImage"
              alt="检测结果"
              class="compare-image"
            />
            <div v-else class="image-placeholder">等待检测...</div>
            <div class="image-label">检测结果</div>
            <div v-if="detectionResult" class="detection-mark"></div>
          </div>
        </div>

        <!-- 批量结果列表 -->
        <div v-if="batchResults.length > 0" class="batch-gallery">
          <div class="gallery-header">
            <span class="gallery-title">批量结果 ({{ batchResults.length }})</span>
          </div>
          <div class="gallery-scroll">
            <div
              v-for="(item, index) in batchResults"
              :key="index"
              class="gallery-item"
              :class="{ active: detectionResult && detectionResult.detection_id === item.detection_id }"
              @click="selectBatchItem(item)"
            >
              <img :src="item.result_image_url" class="gallery-image" />
              <div class="gallery-info">
                <span class="item-count">{{ item.total_objects }} 目标</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧信息面板 -->
      <div class="right-panel">
        <!-- 模型信息 -->
        <div class="info-card">
          <div class="info-item">
            <span class="info-label">检测模型</span>
            <span class="info-value">{{ selectedModel }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">检测类别</span>
            <el-tooltip :content="currentModelClassesFull" placement="top" :show-after="300" popper-class="classes-tooltip">
              <span class="info-value classes-value">{{ currentModelClasses }}</span>
            </el-tooltip>
          </div>
        </div>

        <!-- 识别清单 -->
        <div class="result-card">
          <div class="card-header">
            <el-icon><List /></el-icon>
            <span class="card-title">病虫害清单</span>
          </div>
          <div v-if="detectionResult && detectionResult.boxes && detectionResult.boxes.filter(b => b.confidence > 0).length > 0" class="detection-list">
            <transition-group name="list">
              <div v-for="(box, index) in detectionResult.boxes.filter(b => b.confidence > 0)" :key="index + '-' + box.x1" class="detection-item">
                <span class="item-name">{{ box.chinese_name || box.class_name }}</span>
                <span class="item-conf">{{ (box.confidence * 100).toFixed(1) }}%</span>
              </div>
            </transition-group>
            <div class="total-count">共检测到 {{ detectionResult.boxes.filter(b => b.confidence > 0).length }} 个目标</div>
          </div>

          <div v-else class="empty-state">
            <el-icon class="empty-icon"><CircleCheck /></el-icon>
            <p class="empty-text">未检测到病虫害</p>
            <p class="empty-desc">作物影像无异常或未开始检测</p>
          </div>
        </div>

        <!-- AI诊断建议 -->
        <div class="result-card">
          <div class="card-header">
            <el-icon><ChatDotRound /></el-icon>
            <span class="card-title">AI 诊断建议</span>
          </div>
          <div class="diagnosis-content">
            <p v-if="isDetecting">正在分析中...</p>
            <p v-else-if="detectionResult && activeTab === 'camera'">
              实时监控中... 当前画面检测到 {{ detectionResult.total_objects }} 个目标。系统正以 {{ detectionResult.fps }} FPS 的速率进行动态分析。
            </p>
            <p v-else-if="detectionResult && activeTab === 'video'">
              视频检测已完成，共处理 {{ detectionResult.total_frames }} 帧，累计识别病虫害 {{ detectionResult.total_objects }} 次。您可以播放右侧结果视频查看识别动态。
            </p>
            <p v-else-if="detectionResult && detectionResult.total_objects > 0">
              影像中检测到 {{ detectionResult.total_objects }} 处病虫害，已标记在右侧结果图中，请结合农技指导进行防治。
            </p>
            <p v-else>暂无诊断建议，请先上传并检测作物图片或视频。</p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button size="default" class="btn-secondary">
            <el-icon><Refresh /></el-icon>
            重新检测
          </el-button>
          <el-button type="primary" size="default" class="btn-primary">
            查看防治报告
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 脚本完全保留原 DetectionPage.vue 的逻辑，不做任何修改
import { ref, computed, onMounted } from "vue";
import {
  Picture,
  Plus,
  Folder,
  Monitor,
  Check,
  Grid,
  List,
  CircleCheck,
  ChatDotRound,
  Refresh,
  Minus,
  Loading,
  VideoPlay,
  VideoCamera
} from "@element-plus/icons-vue";
import CameraDetection from "./CameraDetection.vue";
import { ElMessage } from "element-plus";
import { detectSingleImage, detectBatchImages, detectVideo, getAvailableModels } from "../api/detection";

const availableModels = ref([]);
const selectedModel = ref("");
const currentModelClassesFull = computed(() => {
  const model = availableModels.value.find(m => m.name === selectedModel.value);
  return model?.classes?.join(" / ") || "-";
});
const currentModelClasses = computed(() => {
  const model = availableModels.value.find(m => m.name === selectedModel.value);
  const classes = model?.classes || [];
  if (classes.length === 0) return "-";
  if (classes.length <= 4) return classes.join(" / ");
  return `${classes[0]} / ${classes[1]} / ... 等 ${classes.length} 类`;
});
const activeTab = ref("single");
const compareMode = ref("side");
const isDetecting = ref(false);

const originalImage = ref("");
const resultImage = ref("");
const originalVideo = ref("");
const resultVideo = ref("");
const detectionResult = ref(null);
const batchResults = ref([]); // 批量检测结果集
const functionTabs = [
  {
    key: "single",
    name: "单图检测",
    desc: "快速识别一张图片",
    icon: Picture,
    accept: "image/*",
    multiple: false,
  },
  {
    key: "batch",
    name: "批量检测",
    desc: "一次处理多张图片",
    icon: Plus,
    accept: "image/*",
    multiple: true,
  },
  {
    key: "folder",
    name: "文件夹",
    desc: "上传整个文件夹",
    icon: Folder,
    accept: "image/*",
    multiple: true,
    webkitdirectory: true,
  },
  {
    key: "video",
    name: "视频检测",
    desc: "识别视频动态目标",
    icon: VideoPlay,
    accept: "video/*",
    multiple: false,
  },
  {
    key: "camera",
    name: "摄像头",
    desc: "开启实时监控检测",
    icon: VideoCamera,
    accept: "",
    multiple: false,
  },
];

const fileInputs = ref([]);

const handleTabClick = (key) => {
  // 🌟 切换 Tab 时主动清理上一个模式遗留的结果，防止 UI 混乱
  if (activeTab.value !== key) {
    resetDetectionState();
  }
  
  activeTab.value = key;
  const input = document.querySelector(`.function-tab[data-key="${key}"] .file-input`);
  if (input) {
    input.click();
  }
};

// 🌟 抽取统一的状态重置函数
const resetDetectionState = () => {
  originalImage.value = "";
  resultImage.value = "";
  originalVideo.value = "";
  resultVideo.value = "";
  detectionResult.value = null;
  batchResults.value = [];
  isDetecting.value = false;
};

const handleFileChange = async (event, tabKey) => {
  event.stopPropagation();
  event.preventDefault();
  let files = Array.from(event.target.files);
  if (!files || files.length === 0) return;

  // 🌟 在开始新的检测请求前，彻底清空旧数据
  resetDetectionState();
  
  // 过滤掉非影像文件（尤其是文件夹上传时可能带入的系统文件）
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp'];
  const videoExtensions = ['.mp4', '.avi', '.mov', '.mkv'];

  if (tabKey === 'video') {
    files = files.filter(f => videoExtensions.some(ext => f.name.toLowerCase().endsWith(ext)));
  } else {
    files = files.filter(f => imageExtensions.some(ext => f.name.toLowerCase().endsWith(ext)));
  }

  if (files.length === 0) {
    ElMessage.warning("未检测到有效的影像文件，请检查上传内容。");
    return;
  }

  activeTab.value = tabKey;
  isDetecting.value = true;
  // 初始化预览 (已在 resetDetectionState 中重置过，这里根据模式设置预览源)
  if (tabKey === 'single') {
    originalImage.value = URL.createObjectURL(files[0]);
  } else if (tabKey === 'video') {
    originalVideo.value = URL.createObjectURL(files[0]);
  }

  try {
    const baseURL = import.meta.env.VITE_API_BASE_URL ? import.meta.env.VITE_API_BASE_URL.replace('/api', '') : 'http://localhost:8000';
    const getFullUrl = (url) => {
      if (!url) return "";
      if (url.startsWith("http")) return url;
      return baseURL + (url.startsWith("/") ? url : "/" + url);
    };

    if (tabKey === 'single') {
      const formData = new FormData();
      formData.append("file", files[0]);
      formData.append("model_name", selectedModel.value);

      const res = await detectSingleImage(formData);
      if (res.success || res.code === 200) {
        ElMessage.success("检测成功！");
        const data = res.data || res;
        resultImage.value = getFullUrl(data.result_image_url || data.image_url);
        originalImage.value = getFullUrl(data.image_url) || originalImage.value;
        detectionResult.value = data;
      }
    } else if (tabKey === 'video') {
      const formData = new FormData();
      formData.append("file", files[0]);
      formData.append("model_name", selectedModel.value);

      const res = await detectVideo(formData);
      if (res.success || res.code === 200) {
        ElMessage.success("视频检测完成！");
        const data = res.data || res;
        resultVideo.value = getFullUrl(data.result_video_url);
        originalVideo.value = getFullUrl(data.video_url);
        detectionResult.value = {
          ...data,
          boxes: [],
          total_objects: data.total_objects || 0
        };
      }
    } else {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
      }
      formData.append("model_name", selectedModel.value);

      const res = await detectBatchImages(formData);
      if (res.success || res.code === 200) {
        ElMessage.success(`批量检测完成，共 ${res.data.length} 张图片`);
        batchResults.value = res.data.map(item => ({
          ...item,
          image_url: getFullUrl(item.image_url),
          result_image_url: getFullUrl(item.result_image_url)
        }));

        if (batchResults.value.length > 0) {
          const first = batchResults.value[0];
          originalImage.value = first.image_url;
          resultImage.value = first.result_image_url;
          detectionResult.value = first;
        }
      }
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("检测请求失败，请检查后端服务是否正常。");
  } finally {
    isDetecting.value = false;
  }

  setTimeout(() => {
    event.target.value = '';
  }, 0);
};

const selectBatchItem = (item) => {
  originalImage.value = item.image_url;
  resultImage.value = item.result_image_url;
  detectionResult.value = item;
};

onMounted(async () => {
  try {
    const res = await getAvailableModels();
    if (res.success) {
      availableModels.value = res.data;
      if (res.data.length > 0 && !selectedModel.value) {
        selectedModel.value = res.data[0].name;
      }
    }
  } catch (e) {
    console.error("获取模型列表失败:", e);
  }
});

const handleCameraDetected = (data) => {
  detectionResult.value = data;
};
</script>

<style scoped>
/* 农业主题样式（与 LoginPage1.0.vue 保持一致） */
.detection-page {
  min-height: 100vh;
  padding: 32px 48px;
  background-image: url('./background/2.jpg');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  position: relative;
}
.detection-page::before {
  content: "";
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.08);
  pointer-events: none;
  z-index: 0;
}
.page-header, .function-tabs, .main-content, .model-selector {
  position: relative;
  z-index: 2;
}
.page-header {
  margin-bottom: 32px;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(6px);
  border-radius: 24px;
  padding: 28px 32px;
}
.breadcrumb {
  font-size: 16px;
  color: rgba(255,255,240,0.9);
  margin-bottom: 16px;
}
.breadcrumb .active {
  color: #cfb53b;
  font-weight: 600;
}
.page-title {
  font-size: 42px;
  font-weight: 800;
  color: white;
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
  margin-bottom: 12px;
  letter-spacing: 2px;
}
.page-subtitle {
  font-size: 18px;
  color: rgba(255,255,240,0.9);
  font-weight: 500;
  letter-spacing: 1px;
}
.model-selector :deep(.el-select) {
  --el-select-bg-color: transparent;
}
.model-selector :deep(.el-select__wrapper),
.model-selector :deep(.el-input__wrapper) {
  background: rgba(255,252,245,0.55) !important;
  backdrop-filter: blur(10px);
  border-radius: 48px;
  padding: 8px 16px;
  border: none !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}
.model-selector :deep(.el-input) {
  --el-input-bg-color: transparent;
}
.function-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 36px;
  flex-wrap: nowrap;
}
.function-tab {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 16px;
  background: rgba(255,252,245,0.88);
  backdrop-filter: blur(12px);
  border-radius: 60px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid rgba(255,245,215,0.6);
}
.function-tab:hover {
  background: rgba(255,252,245,0.98);
  transform: translateY(-3px);
}
.function-tab.active {
  background: rgba(46,125,50,0.85);
  border-color: #cfb53b;
}
.function-tab.active .tab-text,
.function-tab.active .tab-desc,
.function-tab.active .tab-icon {
  color: white;
}
.tab-icon {
  font-size: 24px;
  color: #2e7d32;
}
.tab-text {
  font-size: 18px;
  font-weight: 700;
  color: #1a3a32;
}
.tab-desc {
  display: none;
}
.file-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}
.main-content {
  display: flex;
  gap: 36px;
  flex-wrap: wrap;
}
.left-panel {
  flex: 2;
  min-width: 360px;
  background: rgba(255,252,245,0.88);
  backdrop-filter: blur(16px);
  border-radius: 48px;
  padding: 32px;
  border: 1px solid rgba(255,245,215,0.6);
}
.panel-header {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 28px;
}
.panel-title {
  font-size: 24px;
  font-weight: 800;
  color: #1a3a32;
}
.result-tag {
  padding: 6px 16px;
  font-size: 14px;
  border-radius: 40px;
}
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.toolbar .el-button {
  border-radius: 40px;
  padding: 10px 20px;
  font-size: 15px;
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(4px);
}
.toolbar .el-button.active {
  background: #2e7d32;
  color: white;
  border-color: #2e7d32;
}
/* 图片对比区域 */
.camera-section {
  margin-top: 24px;
}
.image-compare {
  display: flex;
  gap: 28px;
  flex-wrap: wrap;
}
.image-card {
  flex: 1;
  background: rgba(248,244,235,0.6);
  border-radius: 32px;
  overflow: hidden;
}
.compare-image {
  width: 100%;
  height: auto;
  max-height: 450px;
  object-fit: contain;
  border-radius: 20px;
}
.image-label {
  position: absolute;
  bottom: 32px;
  left: 32px;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(6px);
  color: white;
  padding: 8px 20px;
  border-radius: 60px;
  font-size: 15px;
  font-weight: 500;
}
.detection-mark {
  position: absolute;
  top: 24px;
  right: 24px;
  width: 16px;
  height: 16px;
  background: #cfb53b;
  border-radius: 50%;
  box-shadow: 0 0 0 2px white;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(207,181,59,0.7); }
  70% { box-shadow: 0 0 0 10px rgba(207,181,59,0); }
  100% { box-shadow: 0 0 0 0 rgba(207,181,59,0); }
}
.batch-gallery {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(0,0,0,0.08);
}
.gallery-header {
  margin-bottom: 12px;
}
.gallery-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a3a32;
}
.gallery-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
}
.gallery-item {
  flex-shrink: 0;
  width: 100px;
  height: 100px;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}
.gallery-item.active {
  border-color: #cfb53b;
  box-shadow: 0 4px 6px -1px rgba(207,181,59,0.3);
}
.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.gallery-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.6);
  padding: 4px;
  text-align: center;
}
.item-count {
  color: white;
  font-size: 11px;
}
.right-panel {
  flex: 1;
  min-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.info-card, .result-card {
  background: rgba(255,252,245,0.88);
  backdrop-filter: blur(16px);
  border-radius: 36px;
  padding: 28px;
  border: 1px solid rgba(255,245,215,0.6);
}
.info-item {
  display: flex;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid rgba(0,0,0,0.08);
  font-size: 16px;
}
.info-label {
  color: #5d6e4a;
  font-weight: 600;
}
.info-value {
  font-weight: 700;
  color: #1a3a32;
}
.classes-value {
  cursor: pointer;
  border-bottom: 1px dashed #cfb53b;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  font-weight: 700;
  font-size: 20px;
  border-left: 5px solid #cfb53b;
  padding-left: 16px;
  color: #1a3a32;
}
.empty-state {
  text-align: center;
  padding: 40px;
  background: rgba(248,244,235,0.6);
  border-radius: 32px;
}
.empty-icon {
  font-size: 64px;
  color: #cbd5e1;
  margin-bottom: 16px;
}
.empty-text {
  font-size: 18px;
  font-weight: 600;
  color: #4b5563;
}
.empty-desc {
  font-size: 15px;
  color: #9ca3af;
}
.detection-list {
  max-height: 320px;
  overflow-y: auto;
}
.detection-item {
  display: flex;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid rgba(0,0,0,0.06);
}
.item-name {
  background: #e8f5e9;
  padding: 6px 18px;
  border-radius: 40px;
  font-size: 16px;
  font-weight: 600;
  color: #2e7d32;
}
.item-conf {
  font-family: monospace;
  font-size: 16px;
  font-weight: 700;
  color: #cfb53b;
}
.total-count {
  margin-top: 8px;
  font-size: 14px;
  text-align: right;
  color: #5d6e4a;
}
.diagnosis-content {
  background: rgba(248,244,235,0.7);
  padding: 20px;
  border-radius: 32px;
  color: #1a3a32;
  font-size: 16px;
  line-height: 1.6;
}
.action-buttons {
  display: flex;
  gap: 20px;
  margin-top: 12px;
}
.btn-secondary, .btn-primary {
  flex: 1;
  border-radius: 60px;
  height: 56px;
  font-size: 18px;
  font-weight: 600;
}
.btn-secondary {
  background: white;
  border: 1px solid #cfb53b;
  color: #5d6e4a;
}
.btn-secondary:hover {
  background: #fef5e6;
}
.btn-primary {
  background: linear-gradient(135deg, #1a3a32, #2b5a48);
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}
.model-selector {
  position: absolute;
  top: 28px;
  right: 48px;
  z-index: 10;
}
@media (max-width: 1200px) {
  .detection-page {
    padding: 24px 32px;
  }
  .main-content {
    flex-direction: column;
  }
}
@media (max-width: 768px) {
  .function-tab {
    flex: 1;
    justify-content: center;
  }
  .panel-header {
    flex-direction: column;
  }
}

/* 列表动画 */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
.list-move {
  transition: transform 0.3s ease;
}
</style>

<style>
/* 全局样式：tooltip 宽度限制（不能在 scoped 中生效） */
.classes-tooltip {
  max-width: 360px !important;
  word-break: break-all;
  line-height: 1.6;
}
</style>
