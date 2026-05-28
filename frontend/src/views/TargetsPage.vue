<template>
  <div class="targets-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">病虫害检测库</h1>
      <p class="page-subtitle">平台支持检测的所有农业病虫害类别及其实时识别统计</p>
    </div>

    <!-- 搜索和刷新 -->
    <div class="search-container">
      <el-select v-model="selectedModel" placeholder="选择模型库" class="model-select" @change="fetchTargets">
        <el-option label="害虫识别库 (Best)" value="best" />
        <el-option label="植物病害库 (Last)" value="last" />
      </el-select>
      <el-input
        v-model="searchQuery"
        placeholder="搜索病虫害类别..."
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
          <div class="stat-label">累计识别次数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon category-icon">
          <el-icon><Grid /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ targets.length }}</div>
          <div class="stat-label">核心病虫害类别</div>
        </div>
      </div>
    </div>

    <!-- 病虫害类别列表 -->
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
              color="#2e7d32"
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
      <p class="empty-text">未找到匹配的病虫害类别</p>
    </div>

    <!-- 病虫害详情弹窗 -->
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
            <p>{{ selectedModel === 'last' ? '植物病害智能识别目标' : '农业害虫智能识别目标' }}</p>
          </div>
        </div>

        <el-descriptions :column="1" border class="detail-desc">
          <el-descriptions-item label="目标编号">{{ selectedTarget.id }}</el-descriptions-item>
          <el-descriptions-item label="累计识别">{{ selectedTarget.count }} 次</el-descriptions-item>
          <el-descriptions-item label="模型权重">{{ selectedModel === 'last' ? 'YOLOv11-Plant-Disease-Last' : 'YOLOv11-Pest-Detection-Best' }}</el-descriptions-item>
          <el-descriptions-item label="应用场景">{{ selectedModel === 'last' ? '果园、温室、蔬菜大棚、农田' : '农田、果园、温室、大田作物' }}</el-descriptions-item>
          <el-descriptions-item label="识别特征">
            <template v-if="selectedModel === 'last'">
              <el-tag size="small">病斑特征</el-tag>
              <el-tag size="small" type="warning" style="margin-left: 5px">叶部症状</el-tag>
              <el-tag size="small" type="danger" style="margin-left: 5px">枯萎变色</el-tag>
            </template>
            <template v-else>
              <el-tag size="small">虫体形态</el-tag>
              <el-tag size="small" type="success" style="margin-left: 5px">危害痕迹</el-tag>
              <el-tag size="small" type="warning" style="margin-left: 5px">虫卵分布</el-tag>
            </template>
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
  QuestionFilled,
  Warning,
  WarningFilled,
  CircleCheck,
  Sunny,
  Cloudy,
  Drizzling
} from "@element-plus/icons-vue";
import request from '../utils/request';
import { ElMessage } from "element-plus";

const loading = ref(false);
const searchQuery = ref("");
const selectedModel = ref("best"); // 🌟 默认查看害虫识别库
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
    ElMessage.error("获取病虫害库失败");
  } finally {
    loading.value = false;
  }
};

// 根据病虫害名称返回对应图标
const getIcon = (name) => {
  // 害虫类别
  if (name.includes('蚜虫')) return Cloudy;
  if (name.includes('白粉虱')) return Sunny;
  if (name.includes('潜叶蝇')) return Drizzling;
  if (name.includes('蓟马')) return Promotion;
  if (name.includes('红蜘蛛')) return WarningFilled;
  if (name.includes('粘虫')) return Ship;
  // 植物病害类别
  if (name.includes('健康')) return CircleCheck;
  if (name.includes('病') || name.includes('腐') || name.includes('锈')) return Warning;
  return Aim;
};

const filteredTargets = computed(() => {
  if (!searchQuery.value) return targets.value;
  return targets.value.filter(t => t.name.toLowerCase().includes(searchQuery.value.toLowerCase()));
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

<style scoped>
/* 农业主题统一样式（与 LoginPage1.0 保持一致） */
.targets-page {
  min-height: 100vh;
  padding: 32px 48px;
  background-image: url('./background/4.jpg');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
}

.targets-page::before {
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

.page-header {
  position: relative;
  z-index: 2;
  margin-bottom: 32px;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(6px);
  border-radius: 24px;
  padding: 28px 32px;
}

.page-title {
  font-size: 42px;
  font-weight: 800;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  margin-bottom: 12px;
  letter-spacing: 2px;
}

.page-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 240, 0.9);
  letter-spacing: 1px;
}

.search-container {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 20px;
  margin-bottom: 32px;
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  width: 300px;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(255, 252, 245, 0.95);
  border-radius: 60px;
  padding: 12px 20px;
  border: none;
}

.search-container .el-button {
  border-radius: 40px;
  padding: 12px 24px;
  background: rgba(255, 252, 245, 0.9);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 245, 215, 0.6);
  color: #1a3a32;
}

.search-container .el-button:hover {
  background: #fef5e6;
  transform: translateY(-2px);
}

.stats-cards {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 28px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 220px;
  background: rgba(255, 252, 245, 0.88);
  backdrop-filter: blur(16px);
  border-radius: 36px;
  padding: 28px;
  display: flex;
  align-items: center;
  gap: 24px;
  border: 1px solid rgba(255, 245, 215, 0.6);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
}

.target-icon {
  background: linear-gradient(135deg, #2e7d32, #4caf50);
}

.category-icon {
  background: linear-gradient(135deg, #cfb53b, #e0c45c);
}

.stat-value {
  font-size: 36px;
  font-weight: 800;
  color: #1a3a32;
}

.stat-label {
  font-size: 16px;
  color: #5d6e4a;
  margin-top: 4px;
}

.target-grid {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 28px;
}

.target-card {
  background: rgba(255, 252, 245, 0.88);
  backdrop-filter: blur(16px);
  border-radius: 32px;
  padding: 24px;
  border: 1px solid rgba(255, 245, 215, 0.6);
  cursor: pointer;
  transition: all 0.2s;
}

.target-card:hover {
  transform: translateY(-6px);
  background: rgba(255, 252, 245, 0.96);
  box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.2);
  border-color: #cfb53b;
}

.target-card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.target-icon-wrapper {
  width: 56px;
  height: 56px;
  background: rgba(46, 125, 50, 0.15);
  color: #2e7d32;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.target-name {
  font-size: 20px;
  font-weight: 700;
  color: #1a3a32;
  margin: 0;
  word-break: break-word;
  line-height: 1.3;
}

.target-id {
  font-size: 13px;
  color: #9ca3af;
}

.target-stats .stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.target-stats .stat-label {
  color: #5d6e4a;
  font-size: 14px;
}

.target-stats .stat-count {
  font-weight: 700;
  color: #1a3a32;
}

.target-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #2e7d32;
  font-weight: 600;
}

.empty-state {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 80px 0;
}

.empty-icon {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 24px;
}

.empty-text {
  font-size: 20px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* 弹窗样式覆盖 */
.target-detail {
  text-align: center;
  padding: 20px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.detail-icon-large {
  width: 80px;
  height: 80px;
  background: rgba(46, 125, 50, 0.15);
  color: #2e7d32;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-title h4 {
  font-size: 24px;
  margin: 0;
  color: #1a3a32;
}

.detail-title p {
  color: #5d6e4a;
  margin: 4px 0 0;
}

.detail-desc {
  margin-bottom: 24px;
}

.detail-chart-placeholder {
  background: rgba(248, 244, 235, 0.7);
  padding: 16px;
  border-radius: 20px;
  margin-top: 20px;
}

.detail-chart-placeholder p {
  font-size: 13px;
  color: #5d6e4a;
  margin-bottom: 12px;
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 8px;
  height: 80px;
}

.bar {
  width: 12px;
  background: #c7d2fe;
  border-radius: 6px 6px 0 0;
  transition: background 0.3s;
}

.bar:hover {
  background: #2e7d32;
}

/* 响应式 */
@media (max-width: 768px) {
  .targets-page {
    padding: 24px 24px;
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
    flex-direction: column;
  }
  .target-grid {
    grid-template-columns: 1fr;
  }
}
</style>