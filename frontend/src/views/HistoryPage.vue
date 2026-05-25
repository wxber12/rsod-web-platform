<template>
  <div class="history-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">检测历史记录</h1>
      <p class="page-subtitle">查看和管理您的所有检测记录</p>
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
              {{ record.total_objects }} 个目标
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
            <span class="label">目标数量:</span>
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
      // 简单模拟总数，实际后端应返回总条数
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
    video: "视频检测"
  };
  return map[type] || type;
};

const getTypeTag = (type) => {
  const map = {
    single: "",
    batch: "success",
    video: "warning"
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
    
    // 生成文件名：检测ID_日期.扩展名
    const extension = record.type === 'video' ? 'mp4' : 'jpg';
    link.download = `detection_${record.detection_id.substring(0, 8)}_${new Date().getTime()}.${extension}`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
    
    ElMessage.success("开始下载文件...");
  } catch (error) {
    console.error("下载失败:", error);
    // 降级方案：直接打开
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
.history-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 32px;
    .page-title {
      font-size: 28px;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 8px;
    }
    .page-subtitle {
      color: #6b7280;
      font-size: 16px;
    }
  }

  .search-bar {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    .search-input {
      width: 300px;
    }
    .filter-select {
      width: 160px;
    }
  }

  .history-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
  }

  .history-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    cursor: pointer;
    border: 1px solid #e5e7eb;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .record-preview {
      height: 200px;
      position: relative;
      background: #f3f4f6;
      .preview-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .status-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
        background: rgba(255, 255, 255, 0.9);
        &.completed {
          color: #10b981;
        }
      }
    }

    .record-info {
      padding: 16px;
      .record-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        .record-filename {
          font-weight: 600;
          color: #374151;
          font-size: 14px;
        }
      }
      .record-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        .meta-item {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: #6b7280;
        }
      }
    }

    .record-actions {
      padding: 12px 16px;
      border-top: 1px solid #f3f4f6;
      display: flex;
      justify-content: flex-end;
      gap: 8px;
    }
  }

  .empty-state {
    text-align: center;
    padding: 80px 0;
    .empty-icon {
      color: #e5e7eb;
      margin-bottom: 16px;
    }
    .empty-text {
      color: #9ca3af;
      margin-bottom: 24px;
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 40px;
  }

  /* 详情弹窗样式 */
  .detail-container {
    padding: 10px;
    
    .detail-info-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      background: #f9fafb;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 30px;
      
      .info-item {
        display: flex;
        flex-direction: column;
        gap: 8px;
        
        .label {
          font-size: 13px;
          color: #6b7280;
        }
        
        .value {
          font-size: 15px;
          font-weight: 600;
          color: #1f2937;
        }
      }
    }
    
    .detail-compare {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      
      .compare-box {
        .box-title {
          font-weight: 600;
          margin-bottom: 12px;
          color: #374151;
          display: flex;
          align-items: center;
          gap: 8px;
          
          &::before {
            content: '';
            width: 4px;
            height: 16px;
            background: #4f46e5;
            border-radius: 2px;
          }
        }
        
        .compare-media {
          width: 100%;
          max-height: 500px;
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          object-fit: contain;
          background: #000;
        }
      }
    }
  }
}
</style>
