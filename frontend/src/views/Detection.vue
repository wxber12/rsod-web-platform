<template>
  <div class="detection-container">
    <div class="mode-selector">
      <button
        :class="{ active: compareMode === 'side' }"
        @click="compareMode = 'side'"
      >
        🖼️ 并排对比
      </button>
      <button
        :class="{ active: compareMode === 'slider' }"
        @click="compareMode = 'slider'"
      >
        ↔️ 卷帘对比
      </button>
    </div>

    <div class="display-area">
      <div v-if="compareMode === 'side'" class="side-by-side">
        <div class="image-card">
          <h4>原图</h4>
          <div class="img-wrapper">
            <img v-if="originalImage" :src="originalImage" alt="原图" />
            <div v-else class="placeholder">暂无原图</div>
          </div>
        </div>
        <div class="image-card">
          <h4>AI 标注结果</h4>
          <div class="img-wrapper">
            <img v-if="annotatedImage" :src="annotatedImage" alt="标注图" />
            <div v-else class="placeholder">暂无标注图</div>
          </div>
        </div>
      </div>

      <div v-if="compareMode === 'slider'" class="slider-container">
        <SliderCompare
          v-if="originalImage && annotatedImage"
          :before="originalImage"
          :after="annotatedImage"
        />
        <div v-else class="placeholder">请先上传图片以进行卷帘对比</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
// 导入我们上一步刚整理好的滑块组件
import SliderCompare from '../components/SliderCompare.vue'

// 响应式变量定义
const compareMode = ref('side') // 默认显示 'side'(并排) 或可选 'slider'(滑块)

// 临时存放的测试图片（后续换成你上传图片后后端返回的真实 URL）
const originalImage = ref('https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?w=800')
const annotatedImage = ref('https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?w=800&auto=format&fit=crop')
</script>

<style scoped>
.detection-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

/* 切换按钮样式 */
.mode-selector {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 25px;
}

.mode-selector button {
  padding: 10px 20px;
  font-size: 14px;
  border: 1px solid #dcdfe6;
  background-color: #fff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.mode-selector button:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.mode-selector button.active {
  color: #fff;
  background-color: #409eff;
  border-color: #409eff;
}

/* 并排布局样式 */
.side-by-side {
  display: flex;
  gap: 20px;
  justify-content: space-between;
}

.image-card {
  flex: 1;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  text-align: center;
}

.image-card h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
}

.img-wrapper {
  height: 400px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* 卷帘容器样式 */
.slider-container {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

/* 占位图提示样式 */
.placeholder {
  color: #909399;
  font-size: 14px;
}
</style>