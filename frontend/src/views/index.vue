<template>
  <div class="rsod-container">
    <div class="card">
      <h1 class="title">🛸 RSOD 遥感目标检测平台</h1>
      <p class="subtitle">欢迎来到系统首页，当前页面：检测页面 (index.vue)</p>

      <div class="divider"></div>

      <div class="test-section">
        <h3>🔗 前后端连通性测试</h3>
        <button @click="testConnection" :disabled="loading" class="btn">
          {{ loading ? '连接中...' : '测试与后端连接' }}
        </button>

        <div v-if="responseText" :class="['response-box', isSuccess ? 'success' : 'error']">
          <p><strong>状态码:</strong> {{ responseStatus }}</p>
          <p><strong>返回数据:</strong> {{ responseText }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const loading = ref(false)
const responseText = ref('')
const responseStatus = ref('')
const isSuccess = ref(false)

async function testConnection() {
  loading.value = true
  responseText.value = ''

  try {
    // 请求你刚才用 uvicorn 启动的 FastAPI 后端地址
    const response = await fetch('http://127.0.0.1:8000/api/test/connect')
    responseStatus.value = response.status

    if (response.ok) {
      const data = await response.json()
      responseText.value = data.message // 应该显示 "前后端连通成功！"
      isSuccess.value = true
    } else {
      responseText.value = '服务器返回错误'
      isSuccess.value = false
    }
  } catch (error) {
    responseStatus.value = '连接失败'
    responseText.value = '无法连接到后端服务器，请检查 FastAPI (uvicorn) 是否已启动，且端口为 8000。'
    isSuccess.value = false
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.rsod-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  background-color: #f5f7fa;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.title {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 28px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 14px;
}

.divider {
  height: 1px;
  background: #00000010;
  margin: 30px 0;
}

.test-section h3 {
  color: #34495e;
  margin-bottom: 15px;
}

.btn {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn:hover {
  background-color: #3aa876;
}

.btn:disabled {
  background-color: #a8d8c2;
  cursor: not-allowed;
}

.response-box {
  margin-top: 20px;
  padding: 15px;
  border-radius: 6px;
  text-align: left;
  font-size: 14px;
}

.response-box p {
  margin: 5px 0;
}

.success {
  background-color: #e8f8f5;
  border: 1px solid #a3e4d7;
  color: #117a65;
}

.error {
  background-color: #feadad20;
  border: 1px solid #f99;
  color: #c0392b;
}
</style>