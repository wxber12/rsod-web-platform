<template>
  <div class="container">
    <h1>🎯 目标检测系统</h1>

    <el-upload
      class="upload-area"
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      :before-upload="beforeUpload"
    >
      <el-button type="primary">选择图片上传</el-button>
      <template #tip>
        <div class="el-upload__tip">支持 jpg/png 格式，大小不超过 5MB</div>
      </template>
    </el-upload>

    <el-button
      type="success"
      style="margin-top: 20px"
      @click="handleInference"
      :disabled="!selectedFile || loading"
    >
      {{ loading ? "检测中..." : "开始检测" }}
    </el-button>

    <div v-if="resultImageUrl" class="result-container">
      <h3>检测结果：</h3>
      <img :src="resultImageUrl" alt="检测结果" class="result-img" />

      <div class="detections-list">
        <el-tag
          v-for="(item, index) in detections"
          :key="index"
          type="success"
        >
          {{ item.class }}: {{ (item.confidence * 100).toFixed(1) }}%
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";

// 响应式状态
const selectedFile = ref(null);
const loading = ref(false);
const resultImageUrl = ref("");
const detections = ref([]);

// 文件选择回调
const handleFileChange = (file) => {
  selectedFile.value = file.raw;
  resultImageUrl.value = "";
  detections.value = [];
};

// 上传前校验
const beforeUpload = (file) => {
  const isImage = ["image/jpeg", "image/png"].includes(file.type);
  const isLt5M = file.size / 1024 / 1024 < 5;

  if (!isImage) {
    ElMessage.error("请上传 jpg/png 格式图片");
    return false;
  }
  if (!isLt5M) {
    ElMessage.error("图片大小不能超过 5MB");
    return false;
  }
  return true;
};

// 调用推理接口
const handleInference = async () => {
  if (!selectedFile.value) return;

  loading.value = true;
  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    // 请求刚才 YOLOv11 写的单图推理接口
    const res = await axios.post("http://localhost:8000/api/inference/single", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    if (res.data.code === 200) {
      ElMessage.success("推理成功！");
      // 获取后端返回的 static/results/latest 标注图 URL
      resultImageUrl.value = res.data.data.image_url;
      // 获取识别到的物体数组（含 bbox、置信度等）
      detections.value = res.data.data.detections;
    } else {
      ElMessage.error(res.data.message || "推理失败");
    }
  } catch (err) {
    ElMessage.error(`请求失败: ${err.message}`);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.container {
  text-align: center;
  padding: 50px;
}

.upload-area {
  margin: 20px 0;
}

.result-container {
  margin-top: 30px;
}

.result-img {
  max-width: 800px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.detections-list {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}
</style>