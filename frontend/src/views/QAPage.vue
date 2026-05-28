<template>
  <div class="qa-page">
    <div class="page-header">
      <h1 class="page-title">AI 智能问答</h1>
      <p class="page-subtitle">关于农业病虫害识别的任何问题，都可以问我</p>
    </div>

    <div class="chat-container">
      <div class="chat-messages" ref="messageContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'ai'"><ChatDotRound /></el-icon>
            <el-icon v-else><User /></el-icon>
          </div>
          <div class="message-content">
            {{ msg.content }}
          </div>
        </div>
        <div v-if="sending" class="message ai-message">
          <div class="message-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-content loading">
            <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="question"
          placeholder="请输入你的问题..."
          type="textarea"
          :rows="3"
          @keyup.enter.ctrl="sendMessage"
        />
        <el-button
          type="primary"
          class="send-btn"
          :loading="sending"
          @click="sendMessage"
          :disabled="!question.trim()"
        >
          发送
        </el-button>
      </div>
      <div class="input-tip">
        按 Ctrl + Enter 快速发送
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from "vue";
import { ChatDotRound, User } from "@element-plus/icons-vue";
import { aiService } from "../api/ai_service";
import { ElMessage } from "element-plus";

const question = ref("");
const sending = ref(false);
const messageContainer = ref(null);
const messages = ref([
  {
    role: 'ai',
    content: "你好！我是农业病虫害识别AI助手。我可以帮你解答关于苹果疮痂病、玉米锈病、葡萄黑腐病、番茄早疫病等各类作物病虫害的识别与防治问题，也可以为你提供检测结果的详细分析和防治建议。"
  }
]);

const scrollToBottom = async () => {
  await nextTick();
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
  }
};

watch(messages, () => {
  scrollToBottom();
}, { deep: true });

const sendMessage = async () => {
  if (!question.value.trim() || sending.value) return;

  const currentQuestion = question.value.trim();
  messages.value.push({ role: 'user', content: currentQuestion });
  question.value = "";
  sending.value = true;

  try {
    const history = messages.value.slice(0, -1).map(msg => ({
      role: msg.role === 'ai' ? 'assistant' : 'user',
      content: msg.content
    }));

    const res = await aiService.askQuestion(currentQuestion, history);

    if (res.success) {
      messages.value.push({ role: 'ai', content: res.answer });
    } else {
      throw new Error(res.message || "请求失败");
    }
  } catch (error) {
    console.error("AI 服务请求失败:", error);
    ElMessage.error(error.message || "AI 助手暂时无法回答，请稍后再试");
  } finally {
    sending.value = false;
  }
};

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
/* 农业主题统一样式（与 LoginPage1.0 和 DetectionPage 保持一致） */
.qa-page {
  min-height: 100vh;
  padding: 32px 48px;
  background-image: url('./background/1.jpg');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
}

.qa-page::before {
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
}

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

.chat-container {
  position: relative;
  z-index: 2;
  background: rgba(255, 252, 245, 0.88);
  backdrop-filter: blur(16px);
  border-radius: 48px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(255, 245, 215, 0.6);
  height: calc(100vh - 180px);
  min-height: 500px;
}

.chat-messages {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.message {
  display: flex;
  margin-bottom: 28px;
  animation: fadeIn 0.3s ease-in-out;
}

.message-avatar {
  width: 52px;
  height: 52px;
  border-radius: 52px;
  background: linear-gradient(135deg, #1a3a32, #2b5a48);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
  font-size: 28px;
}

.message-content {
  background: #fef9f0;
  padding: 16px 24px;
  border-radius: 28px;
  border-top-left-radius: 8px;
  max-width: 70%;
  line-height: 1.6;
  font-size: 18px;
  color: #1a3a32;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  white-space: pre-wrap;
  word-break: break-word;
}

.message-content.loading {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  animation: blink 1.4s infinite both;
  font-size: 24px;
  line-height: 1;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-avatar {
  margin-right: 0;
  margin-left: 16px;
  background: #cfb53b;
}

.user-message .message-content {
  background: #e8f5e9;
  border-radius: 28px;
  border-top-right-radius: 8px;
  color: #1a3a32;
}

.chat-input {
  padding: 28px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  gap: 20px;
  background: rgba(255, 252, 245, 0.9);
}

.chat-input :deep(.el-textarea__inner) {
  background-color: rgba(254, 249, 240, 0.9);
  border-radius: 30px;
  border: 1px solid #E5DAC8;
  transition: all 0.2s;
  padding: 12px 20px;
  font-size: 16px;
  resize: none;
}

.chat-input :deep(.el-textarea__inner:focus) {
  border-color: #1A3A32;
  box-shadow: 0 0 0 3px rgba(26, 58, 50, 0.1);
}

.send-btn {
  width: 120px;
  border-radius: 60px;
  background: linear-gradient(135deg, #1a3a32, #2b5a48);
  border: none;
  font-size: 18px;
  font-weight: 600;
  transition: all 0.3s;
}

.send-btn:hover {
  background: linear-gradient(135deg, #2b5a48, #1a3a32);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(26, 58, 50, 0.3);
}

.input-tip {
  padding: 0 28px 20px;
  font-size: 13px;
  color: #a08c5e;
  text-align: right;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes blink {
  0% { opacity: 0.2; }
  20% { opacity: 1; }
  100% { opacity: 0.2; }
}

@media (max-width: 768px) {
  .qa-page {
    padding: 24px 24px;
  }
  .message-content {
    max-width: 85%;
    font-size: 16px;
  }
  .chat-messages {
    padding: 20px;
  }
  .chat-input {
    padding: 20px;
    flex-direction: column;
  }
  .send-btn {
    width: 100%;
    height: 48px;
  }
}
</style>