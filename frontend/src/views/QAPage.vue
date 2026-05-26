<template>
  <div class="qa-page">
    <div class="page-header">
      <h1 class="page-title">AI 智能问答</h1>
      <p class="page-subtitle">关于遥感目标检测的任何问题，都可以问我</p>
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
    content: "你好！我是遥感目标检测AI助手。我可以帮你解答关于飞机、油罐、操场、立交桥、农业病虫害等遥感目标检测的相关问题，也可以为你提供检测结果的详细分析。" 
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
    // 移除刚才发送失败的消息，或者保留并显示错误？
    // 这里简单处理，不移除，让用户知道发了什么
  } finally {
    sending.value = false;
  }
};

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped lang="scss">
.qa-page {
  width: 100%;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;

  .page-header {
    margin-bottom: 24px;
    flex-shrink: 0;

    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 8px;
    }

    .page-subtitle {
      font-size: 14px;
      color: #6b7280;
    }
  }

  .chat-container {
    flex: 1;
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid #e5e7eb;

    .chat-messages {
      flex: 1;
      padding: 24px;
      overflow-y: auto;
      scroll-behavior: smooth;

      .message {
        display: flex;
        margin-bottom: 24px;
        animation: fadeIn 0.3s ease-in-out;

        .message-avatar {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          background-color: #4f46e5;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 12px;
          flex-shrink: 0;
          font-size: 20px;
        }

        .message-content {
          background-color: #f3f4f6;
          padding: 12px 16px;
          border-radius: 0 16px 16px 16px;
          max-width: 80%;
          line-height: 1.6;
          font-size: 15px;
          color: #374151;
          white-space: pre-wrap;
          word-break: break-word;

          &.loading {
            display: flex;
            align-items: center;
            gap: 4px;
            
            .dot {
              animation: blink 1.4s infinite both;
              &:nth-child(2) { animation-delay: 0.2s; }
              &:nth-child(3) { animation-delay: 0.4s; }
            }
          }
        }

        &.user-message {
          flex-direction: row-reverse;

          .message-avatar {
            margin-right: 0;
            margin-left: 12px;
            background-color: #10b981;
          }

          .message-content {
            background-color: #4f46e5;
            color: white;
            border-radius: 16px 0 16px 16px;
          }
        }
      }
    }

    .chat-input {
      padding: 20px;
      border-top: 1px solid #e5e7eb;
      display: flex;
      gap: 12px;
      background-color: #f9fafb;

      :deep(.el-textarea__inner) {
        border-radius: 8px;
        resize: none;
        &:focus {
          border-color: #4f46e5;
        }
      }

      .send-btn {
        height: auto;
        padding: 0 24px;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;

        &:not(:disabled):hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.4);
        }
      }
    }

    .input-tip {
      padding: 0 20px 12px;
      font-size: 12px;
      color: #9ca3af;
      text-align: right;
      background-color: #f9fafb;
    }
  }
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
</style>
