<template>
  <div class="history-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">检测历史记录</h1>
      <p class="page-subtitle">查看和管理您的所有病虫害检测记录</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索检测记录..."
        size="default"
        class="search-input"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select
        v-model="filterType"
        placeholder="类型筛选"
        size="default"
        class="filter-select"
        clearable
      >
        <el-option label="全部类型" value="" />
        <el-option label="单图检测" value="single" />
        <el-option label="批量检测" value="batch" />
        <el-option label="视频检测" value="video" />
        <el-option label="摄像头检测" value="camera" />
      </el-select>

      <el-button type="primary" plain @click="fetchHistory">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 记录列表 -->
    <div v-loading="loading" class="history-list">
      <div
        v-for="record in filteredRecords"
        :key="record.detection_id"
        class="history-card"
        @click="viewRecord(record)"
      >
        <div class="record-preview">
          <video
            v-if="record.type === 'video'"
            :src="getFullUrl(record.result_image_url)"
            class="preview-image"
            muted
          />
          <img
            v-else
            :src="getFullUrl(record.result_image_url)"
            class="preview-image"
          />
          <div class="status-badge completed">
            <el-icon><CircleCheck /></el-icon>
            已完成
          </div>
        </div>

        <div class="record-info">
          <div class="record-header">
            <span class="record-filename">检测编号: {{ record.detection_id.substring(0, 8) }}...</span>
            <el-tag :type="getTypeTag(record.type)" size="small">{{ getTypeText(record.type) }}</el-tag>
          </div>
          <div class="record-meta">
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatDate(record.created_at) }}
            </span>
            <span class="meta-item">
              <el-icon><Aim /></el-icon>
              {{ record.total_objects }} 处病虫害
            </span>
            <span class="meta-item">
              <el-icon><Timer /></el-icon>
              {{ record.detection_time }}s
            </span>
            <span class="meta-item">
              <el-icon><Cpu /></el-icon>
              {{ record.model_name }}
            </span>
          </div>
        </div>

        <div class="record-actions">
          <el-button size="small" type="primary" plain @click.stop="viewRecord(record)">
            <el-icon><Monitor/></el-icon>
            查看详情
          </el-button>
          <el-button size="small" type="success" plain @click.stop="downloadResult(record)">
            <el-icon><Download/></el-icon>
            保存结果
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && filteredRecords.length === 0" class="empty-state">
      <el-icon :size="64" class="empty-icon"><Help /></el-icon>
      <p class="empty-text">暂无相关检测记录</p>
      <el-button type="primary" @click="goToDetection">
        <el-icon><Plus /></el-icon>
        去开启新检测
      </el-button>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-if="totalRecords > 0"
        v-model:current-page="currentPage"
        :total="totalRecords"
        :page-size="pageSize"
        @current-change="handlePageChange"
        layout="prev, pager, next"
        background
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="检测结果详情"
      width="80%"
      destroy-on-close
      class="detail-dialog"
    >
      <div v-if="currentDetail" class="detail-container">
        <div class="detail-info-grid">
          <div class="info-item">
            <span class="label">检测编号:</span>
            <span class="value">{{ currentDetail.detection_id }}</span>
          </div>
          <div class="info-item">
            <span class="label">检测类型:</span>
            <el-tag :type="getTypeTag(currentDetail.type)">{{ getTypeText(currentDetail.type) }}</el-tag>
          </div>
          <div class="info-item">
            <span class="label">检测时间:</span>
            <span class="value">{{ formatDate(currentDetail.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">病虫害数量:</span>
            <span class="value">{{ currentDetail.total_objects }}</span>
          </div>
          <div class="info-item">
            <span class="label">推理耗时:</span>
            <span class="value">{{ currentDetail.detection_time }}s</span>
          </div>
          <div class="info-item">
            <span class="label">使用模型:</span>
            <span class="value">{{ currentDetail.model_name }}</span>
          </div>
        </div>

        <div class="detail-compare">
          <div class="compare-box">
            <div class="box-title">原始文件</div>
            <video
              v-if="currentDetail.type === 'video'"
              :src="getFullUrl(currentDetail.image_url)"
              controls
              class="compare-media"
            />
            <img
              v-else
              :src="getFullUrl(currentDetail.image_url)"
              class="compare-media"
            />
          </div>
          <div class="compare-box">
            <div class="box-title">识别结果</div>
            <video
              v-if="currentDetail.type === 'video'"
              :src="getFullUrl(currentDetail.result_image_url)"
              controls
              class="compare-media"
            />
            <img
              v-else
              :src="getFullUrl(currentDetail.result_image_url)"
              class="compare-media"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="success" @click="downloadResult(currentDetail)">
          <el-icon><Download /></el-icon>
          下载结果
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// 脚本部分完全保留原逻辑，不做任何修改
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  Search,
  Clock,
  Aim,
  Monitor,
  Download,
  Plus,
  Help,
  CircleCheck,
  Timer,
  Cpu,
  Refresh
} from "@element-plus/icons-vue";
import { getDetectionHistory, getDetectionDetail } from "../api/detection";
import { ElMessage } from "element-plus";

const router = useRouter();
const loading = ref(false);
const searchQuery = ref("");
const filterType = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const totalRecords = ref(0);
const historyRecords = ref([]);

const detailVisible = ref(false);
const currentDetail = ref(null);

const getFullUrl = (url) => {
  if (!url) return "";
  if (url.startsWith("http")) return url;
  const baseURL = import.meta.env.VITE_API_BASE_URL ? import.meta.env.VITE_API_BASE_URL.replace('/api', '') : 'http://localhost:8000';
  return baseURL + (url.startsWith("/") ? url : "/" + url);
};

const fetchHistory = async () => {
  loading.value = true;
  try {
    const res = await getDetectionHistory({
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value
    });
    if (res.success) {
      historyRecords.value = res.data;
      totalRecords.value = res.data.length === pageSize.value ? currentPage.value * pageSize.value + 1 : historyRecords.value.length;
    }
  } catch (error) {
    ElMessage.error("获取历史记录失败");
  } finally {
    loading.value = false;
  }
};

const filteredRecords = computed(() => {
  return historyRecords.value.filter((record) => {
    const matchesSearch = !searchQuery.value || record.detection_id.includes(searchQuery.value);
    const matchesType = !filterType.value || record.type === filterType.value;
    return matchesSearch && matchesType;
  });
});

const getTypeText = (type) => {
  const map = {
    single: "单图检测",
    batch: "批量检测",
    video: "视频检测",
    camera: "实时监控"
  };
  return map[type] || type;
};

const getTypeTag = (type) => {
  const map = {
    single: "",
    batch: "success",
    video: "warning",
    camera: "danger"
  };
  return map[type] || "";
};

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return date.toLocaleString();
};

const handlePageChange = (page) => {
  currentPage.value = page;
  fetchHistory();
};

const viewRecord = async (record) => {
  loading.value = true;
  try {
    const res = await getDetectionDetail(record.detection_id);
    if (res.success) {
      currentDetail.value = res.data;
      detailVisible.value = true;
    }
  } catch (error) {
    ElMessage.error("获取详情失败");
  } finally {
    loading.value = false;
  }
};

const downloadResult = async (record) => {
  if (!record) return;
  const url = getFullUrl(record.result_image_url);

  try {
    const response = await fetch(url);
    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = blobUrl;

    const extension = record.type === 'video' ? 'mp4' : 'jpg';
    link.download = `detection_${record.detection_id.substring(0, 8)}_${new Date().getTime()}.${extension}`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);

    ElMessage.success("开始下载文件...");
  } catch (error) {
    console.error("下载失败:", error);
    window.open(url, '_blank');
  }
};

const goToDetection = () => {
  router.push({ name: "Detection" });
};

onMounted(() => {
  fetchHistory();
});
</script>

<style scoped lang="scss">
/* 农业主题统一样式（与 LoginPage1.0 和 DetectionPage 保持一致） */
.history-page {
  min-height: 100vh;
  padding: 32px 48px;
  background-image: url('./background/0.jpg');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;

  &::before {
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

  .page-header,
  .search-bar,
  .history-list,
  .pagination-wrapper {
    position: relative;
    z-index: 2;
  }

  .page-header {
    margin-bottom: 32px;
    .page-title {
      font-size: 42px;
      font-weight: 800;
      color: white;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      margin-bottom: 12px;
      letter-spacing: -0.5px;
    }
    .page-subtitle {
      font-size: 18px;
      color: rgba(255, 255, 240, 0.9);
    }
  }

  .search-bar {
    display: flex;
    gap: 20px;
    margin-bottom: 32px;
    flex-wrap: wrap;
    align-items: center;

    .search-input {
      width: 300px;
      :deep(.el-input__wrapper) {
        background: rgba(255, 252, 245, 0.95);
        border-radius: 60px;
        padding: 12px 20px;
        border: none;
      }
    }
    .filter-select {
      width: 160px;
      :deep(.el-input__wrapper) {
        background: rgba(255, 252, 245, 0.95);
        border-radius: 60px;
        padding: 12px 20px;
        border: none;
      }
    }
    .el-button {
      border-radius: 40px;
      padding: 12px 24px;
      background: rgba(255, 252, 245, 0.9);
      backdrop-filter: blur(4px);
      border: 1px solid rgba(255, 245, 215, 0.6);
      &:hover {
        background: #fef5e6;
        transform: translateY(-2px);
      }
    }
  }

  .history-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 28px;
    margin-bottom: 40px;
  }

  .history-card {
    background: rgba(255, 252, 245, 0.88);
    backdrop-filter: blur(16px);
    border-radius: 32px;
    overflow: hidden;
    transition: all 0.2s;
    border: 1px solid rgba(255, 245, 215, 0.6);
    cursor: pointer;

    &:hover {
      transform: translateY(-6px);
      background: rgba(255, 252, 245, 0.96);
      box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.2);
    }

    .record-preview {
      height: 200px;
      position: relative;
      background: #2d3e2b;
      .preview-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .status-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(4px);
        color: #cfb53b;
        &.completed {
          color: #2e7d32;
          background: rgba(255, 255, 255, 0.9);
        }
      }
    }

    .record-info {
      padding: 20px;
      .record-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        .record-filename {
          font-size: 18px;
          font-weight: 700;
          color: #1a3a32;
        }
      }
      .record-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        .meta-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          color: #5d6e4a;
        }
      }
    }

    .record-actions {
      padding: 16px 20px;
      border-top: 1px solid rgba(0, 0, 0, 0.08);
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      .el-button {
        border-radius: 40px;
        padding: 8px 20px;
        font-size: 14px;
        font-weight: 500;
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 80px 0;
    .empty-icon {
      color: rgba(255, 255, 255, 0.6);
      margin-bottom: 24px;
    }
    .empty-text {
      font-size: 20px;
      font-weight: 600;
      color: white;
      text-shadow: 0 1px 3px rgba(0,0,0,0.2);
      margin-bottom: 24px;
    }
    .el-button {
      border-radius: 60px;
      padding: 12px 28px;
      font-size: 16px;
      background: linear-gradient(135deg, #1a3a32, #2b5a48);
      border: none;
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 40px;
    :deep(.el-pagination) {
      .btn-prev, .btn-next, .el-pager li {
        background: rgba(255, 252, 245, 0.8);
        backdrop-filter: blur(4px);
        border-radius: 30px;
        margin: 0 4px;
        color: #1a3a32;
        &:hover {
          background: #cfb53b;
          color: white;
        }
      }
      .el-pager li.active {
        background: #2e7d32;
        color: white;
      }
    }
  }

  /* 详情弹窗样式 */
  .detail-container {
    padding: 10px;
    .detail-info-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      background: rgba(255, 252, 245, 0.9);
      backdrop-filter: blur(12px);
      padding: 24px;
      border-radius: 32px;
      margin-bottom: 30px;
      .info-item {
        display: flex;
        flex-direction: column;
        gap: 8px;
        .label {
          font-size: 14px;
          color: #5d6e4a;
        }
        .value {
          font-size: 16px;
          font-weight: 600;
          color: #1a3a32;
        }
      }
    }
    .detail-compare {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 28px;
      .compare-box {
        .box-title {
          font-size: 18px;
          font-weight: 700;
          margin-bottom: 16px;
          color: #1a3a32;
          display: flex;
          align-items: center;
          gap: 10px;
          &::before {
            content: '';
            width: 5px;
            height: 20px;
            background: #cfb53b;
            border-radius: 3px;
          }
        }
        .compare-media {
          width: 100%;
          max-height: 500px;
          border-radius: 20px;
          box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
          object-fit: contain;
          background: #1a2a1f;
        }
      }
    }
  }
}
</style>