<template>
  <div class="detection-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="breadcrumb">
        <span>工作台</span>
        <span class="separator">›</span>
        <span class="active">智能检测</span>
      </div>
      <h1 class="page-title">上传遥感影像，立即识别多类目标</h1>
      <p class="page-subtitle">
        支持飞机 / 油罐 / 操场 / 建筑物 / 船舶 / 农业虫害等多目标检测
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
        <div class="tab-content">
          <span class="tab-text">{{ tab.name }}</span>
          <span class="tab-desc">{{ tab.desc }}</span>
        </div>
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
          <CameraDetection @detected="handleCameraDetected" />
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
            <div v-else class="image-placeholder">请上传图片/视频</div>
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
            <span class="card-title">识别清单</span>
          </div>
          
          <div v-if="detectionResult && detectionResult.boxes && detectionResult.boxes.length > 0" class="detection-list">
            <div v-for="(box, index) in detectionResult.boxes" :key="index" class="detection-item">
              <span class="item-name">{{ box.class_name }}</span>
              <span class="item-conf">{{ (box.confidence * 100).toFixed(1) }}%</span>
            </div>
            <div class="total-count">共检测到 {{ detectionResult.total_objects }} 个目标</div>
          </div>
          
          <div v-else class="empty-state">
            <el-icon class="empty-icon"><CircleCheck /></el-icon>
            <p class="empty-text">未检测到目标</p>
            <p class="empty-desc">影像无异常目标或未开始检测</p>
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
              视频检测已完成，共处理 {{ detectionResult.total_frames }} 帧，累计识别目标 {{ detectionResult.total_objects }} 次。您可以播放右侧结果视频查看识别动态。
            </p>
            <p v-else-if="detectionResult && detectionResult.total_objects > 0">
              图像中检测到 {{ detectionResult.total_objects }} 个目标实体，已标记在右侧结果图中，请仔细核对。
            </p>
            <p v-else>暂无诊断建议，请先上传并检测图片或视频。</p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button size="default" class="btn-secondary">
            <el-icon><Refresh /></el-icon>
            重新检测
          </el-button>
          <el-button type="primary" size="default" class="btn-primary">
            查看完整报告
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
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
import { detectSingleImage, detectBatchImages, detectVideo, getAvailableModels } from "../api/detection"; // 引入检测 API

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
const isDetecting = ref(false); // 检测状态

// 响应数据
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
    webkitdirectory: true, // 👈 标记该选项卡需要文件夹选择
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
      // 批量检测
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
        
        // 默认选中第一张作为预览
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

// 获取可用模型列表
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
</script>

<style scoped>
.detection-page {
  width: 100%;
  position: relative;
}

.page-header {
  margin-bottom: 32px;
  padding-top: 0;
}

.breadcrumb {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.separator {
  margin: 0 6px;
}

.active {
  color: var(--text-primary);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.model-selector {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 10;
}

/* 功能选项卡 */
.function-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.function-tab {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background-color: #ffffff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

.function-tab:hover {
  background-color: var(--primary-light);
}

.function-tab.active {
  background-color: var(--primary-light);
  border-color: var(--primary-color);
}

.tab-icon {
  font-size: 18px;
  color: var(--primary-color);
  margin-right: 12px;
  flex-shrink: 0;
}

.tab-content {
  display: flex;
  flex-direction: column;
}

.tab-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.tab-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

/* 主内容区域 */
.main-content {
  display: flex;
  gap: 24px;
}

.left-panel {
  flex: 1;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.result-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.toolbar .el-button {
  border-radius: 6px;
  padding: 6px 14px;
}

.toolbar .el-button.active {
  background-color: var(--primary-light);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

/* 图片对比区域 */
.camera-section {
  margin-top: 24px;
}

.image-compare {
  display: flex;
  gap: 16px;
  height: 320px;
}

.image-card {
  flex: 1;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f9fafb;
}

.compare-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  font-size: 13px;
}

.detection-mark {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detection-mark::after {
  content: "✓";
  color: #ffffff;
  font-size: 18px;
  font-weight: bold;
}

/* 批量图库样式 */
.batch-gallery {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f3f4f6;
}

.gallery-header {
  margin-bottom: 12px;
}

.gallery-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.gallery-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: thin;
  scrollbar-color: #e5e7eb transparent;
}

.gallery-scroll::-webkit-scrollbar {
  height: 6px;
}

.gallery-scroll::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 3px;
}

.gallery-item {
  flex-shrink: 0;
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.gallery-item:hover {
  transform: translateY(-2px);
}

.gallery-item.active {
  border-color: #4f46e5;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
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
  background: rgba(0, 0, 0, 0.6);
  padding: 2px 4px;
  text-align: center;
}

.item-count {
  color: white;
  font-size: 10px;
}

/* 右侧面板 */
.right-panel {
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.classes-value {
  cursor: pointer;
  border-bottom: 1px dashed var(--text-secondary);
}

.result-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.card-header .el-icon {
  font-size: 16px;
  color: var(--primary-color);
  margin-right: 8px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0;
}

.empty-icon {
  font-size: 48px;
  color: var(--success-color);
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.empty-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: 14px;
  background-color: #f3f4f6;
}

.detection-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detection-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f9fafb;
  border-radius: 6px;
  font-size: 13px;
}

.item-name {
  color: var(--text-primary);
  font-weight: 500;
}

.item-conf {
  color: var(--primary-color);
  font-weight: 600;
}

.total-count {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  text-align: right;
}

.diagnosis-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  flex: 1;
  border-radius: 8px;
  padding: 10px;
  font-size: 14px;
}

.btn-primary {
  flex: 2;
  border-radius: 8px;
  padding: 10px;
  font-size: 14px;
}
</style>

<style>
.classes-tooltip {
  max-width: 360px !important;
  word-break: break-all;
}
</style>