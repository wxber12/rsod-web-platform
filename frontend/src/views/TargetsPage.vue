<template>
  <div class="targets-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">目标检测库</h1>
      <p class="page-subtitle">平台支持检测的所有遥感目标类别及其实时识别统计</p>
    </div>

    <!-- 搜索和刷新 -->
    <div class="search-container">
      <el-select v-model="selectedModel" placeholder="选择模型库" class="model-select" @change="fetchTargets">
        <el-option label="遥感目标库 (Best)" value="best" />
        <el-option label="植物病害库 (Last)" value="last" />
      </el-select>
      <el-input
        v-model="searchQuery"
        placeholder="搜索目标类别..."
        size="default"
        class="search-input"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" plain @click="fetchTargets">
        <el-icon><Refresh /></el-icon> 刷新统计
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-loading="loading">
      <div class="stat-card">
        <div class="stat-icon target-icon">
          <el-icon><Aim /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalDetectionsCount }}</div>
          <div class="stat-label">累计检测实例</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon category-icon">
          <el-icon><Grid /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ targets.length }}</div>
          <div class="stat-label">核心检测类别</div>
        </div>
      </div>
    </div>

    <!-- 目标类别列表 -->
    <div class="target-grid" v-loading="loading">
      <div
        v-for="target in filteredTargets"
        :key="target.id"
        class="target-card"
        @click="showTargetDetail(target)"
      >
        <div class="target-card-header">
          <div class="target-icon-wrapper">
            <el-icon :size="24"><component :is="getIcon(target.name)" /></el-icon>
          </div>
          <div class="target-main-info">
            <h3 class="target-name">{{ target.name }}</h3>
            <span class="target-id">ID: #{{ target.id }}</span>
          </div>
        </div>
        <div class="target-stats">
          <div class="stat-item">
            <span class="stat-label">识别总数</span>
            <span class="stat-count">{{ target.count }}</span>
          </div>
          <div class="stat-progress">
            <el-progress 
              :percentage="Math.min(100, (target.count / Math.max(...targets.map(t => t.count)) * 100))" 
              :show-text="false"
              :stroke-width="6"
              color="#4f46e5"
            />
          </div>
        </div>
        <div class="target-footer">
          <span>查看详情分析</span>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && filteredTargets.length === 0" class="empty-state">
      <el-icon :size="64" class="empty-icon"><Help /></el-icon>
      <p class="empty-text">未找到匹配的目标类别</p>
    </div>

    <!-- 目标详情弹窗 -->
    <el-dialog
      v-model="showDialog"
      :title="selectedTarget?.name + ' - 类别详情'"
      width="500px"
      destroy-on-close
    >
      <div v-if="selectedTarget" class="target-detail">
        <div class="detail-header">
          <div class="detail-icon-large">
            <el-icon :size="48"><component :is="getIcon(selectedTarget.name)" /></el-icon>
          </div>
          <div class="detail-title">
            <h4>{{ selectedTarget.name }}</h4>
            <p>RSOD 标准识别目标</p>
          </div>
        </div>
        
        <el-descriptions :column="1" border class="detail-desc">
          <el-descriptions-item label="目标编号">{{ selectedTarget.id }}</el-descriptions-item>
          <el-descriptions-item label="累计识别">{{ selectedTarget.count }} 次</el-descriptions-item>
          <el-descriptions-item label="模型权重">YOLOv11-RSOD-Best</el-descriptions-item>
          <el-descriptions-item label="应用场景">卫星遥感、航拍影像、城市规划</el-descriptions-item>
          <el-descriptions-item label="识别特征">
            <el-tag size="small">形状特征</el-tag>
            <el-tag size="small" type="success" style="margin-left: 5px">纹理识别</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-chart-placeholder">
          <p>识别频次趋势分析 (模拟数据)</p>
          <div class="mini-chart">
            <div v-for="i in 10" :key="i" class="bar" :style="{ height: Math.random() * 60 + 20 + 'px' }"></div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  Search,
  Aim,
  Grid,
  Help,
  Refresh,
  ArrowRight,
  Ship,
  Location,
  Promotion,
  Box,
  Sugar,
  QuestionFilled
} from "@element-plus/icons-vue";
import request from '../utils/request';
import { ElMessage } from "element-plus";

const loading = ref(false);
const searchQuery = ref("");
const selectedModel = ref("best"); // 🌟 默认查看遥感库
const showDialog = ref(false);
const selectedTarget = ref(null);
const targets = ref([]);

const fetchTargets = async () => {
  loading.value = true;
  try {
    const res = await request.get('/detection/targets/list', {
      params: { model_name: selectedModel.value }
    });
    if (res.success) {
      targets.value = res.data;
    } else {
      ElMessage.warning(res.message || "后端未返回有效数据");
    }
  } catch (error) {
    ElMessage.error("获取目标库失败");
  } finally {
    loading.value = false;
  }
};

const getIcon = (name) => {
  if (name.includes('飞机')) return Promotion;
  if (name.includes('油罐')) return Box;
  if (name.includes('桥')) return Location;
  if (name.includes('操场')) return Aim;
  if (name.includes('苹果') || name.includes('番茄') || name.includes('健康')) return Sugar;
  return Aim;
};

const filteredTargets = computed(() => {
  if (!searchQuery.value) return targets.value;
  return targets.value.filter(t => t.name.includes(searchQuery.value));
});

const totalDetectionsCount = computed(() => {
  return targets.value.reduce((sum, t) => sum + t.count, 0);
});

const showTargetDetail = (target) => {
  selectedTarget.value = target;
  showDialog.value = true;
};

onMounted(() => {
  fetchTargets();
});
</script>

<style scoped lang="scss">
.targets-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 32px;
    .page-title {
      font-size: 28px;
      font-weight: 700;
      color: #1f2937;
    }
    .page-subtitle {
      color: #6b7280;
      margin-top: 8px;
    }
  }

  .search-container {
    display: flex;
    gap: 16px;
    margin-bottom: 32px;
    
    .model-select {
      width: 180px;
    }
    
    .search-input {
      width: 300px;
    }
  }

  .stats-cards {
    display: flex;
    gap: 24px;
    margin-bottom: 40px;

    .stat-card {
      flex: 1;
      background: white;
      border-radius: 12px;
      padding: 24px;
      display: flex;
      align-items: center;
      gap: 20px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      border: 1px solid #e5e7eb;

      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        
        &.target-icon { background: linear-gradient(135deg, #4f46e5, #818cf8); }
        &.category-icon { background: linear-gradient(135deg, #10b981, #34d399); }
      }

      .stat-value {
        font-size: 24px;
        font-weight: 700;
        color: #111827;
      }
      .stat-label {
        font-size: 14px;
        color: #6b7280;
        margin-top: 4px;
      }
    }
  }

  .target-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
  }

  .target-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #e5e7eb;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      border-color: #4f46e5;
    }

    .target-card-header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;

      .target-icon-wrapper {
        width: 48px;
        height: 48px;
        background: #f5f3ff;
        color: #4f46e5;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .target-name {
        font-size: 18px;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
      }
      .target-id {
        font-size: 12px;
        color: #9ca3af;
      }
    }

    .target-stats {
      .stat-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        .stat-label { color: #6b7280; font-size: 14px; }
        .stat-count { font-weight: 700; color: #111827; }
      }
    }

    .target-footer {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid #f3f4f6;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #4f46e5;
      font-size: 13px;
      font-weight: 500;
    }
  }

  .target-detail {
    .detail-header {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 24px;
      
      .detail-icon-large {
        width: 80px;
        height: 80px;
        background: #f5f3ff;
        color: #4f46e5;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      h4 { font-size: 22px; margin: 0; color: #111827; }
      p { color: #6b7280; margin: 4px 0 0; }
    }

    .detail-desc {
      margin-bottom: 24px;
    }

    .detail-chart-placeholder {
      background: #f9fafb;
      padding: 16px;
      border-radius: 12px;
      text-align: center;
      
      p { font-size: 13px; color: #6b7280; margin-bottom: 12px; }
      
      .mini-chart {
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 6px;
        height: 80px;
        
        .bar {
          width: 12px;
          background: #c7d2fe;
          border-radius: 4px 4px 0 0;
          transition: background 0.3s;
          &:hover { background: #4f46e5; }
        }
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 60px 0;
    color: #9ca3af;
  }
}
</style>
