<template>
  <div class="forgot-container">
    <div class="forgot-card">
      <div class="card-inner">
        <div class="brand">
          <div class="logo-icon">
            <el-icon :size="56" color="#CFB53B"><Lock /></el-icon>
          </div>
          <h1 class="title">重置密码</h1>
          <p class="subtitle">输入注册邮箱，获取重置链接</p>
        </div>

        <el-form ref="forgotFormRef" :model="forgotForm" :rules="forgotRules" class="forgot-form">
          <el-form-item prop="email">
            <el-input
              v-model="forgotForm.email"
              type="email"
              placeholder="注册邮箱"
              size="large"
              class="custom-input"
              @keyup.enter="handleSubmit"
            >
              <template #prefix><el-icon><Message /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-button type="primary" size="large" class="submit-btn" :loading="isLoading" @click="handleSubmit">
            发送重置链接
          </el-button>
        </el-form>

        <div class="back-prompt">
          <router-link to="/login" class="back-link">← 返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { Lock, Message } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { forgotPassword } from "../api/auth";

const router = useRouter();
const forgotFormRef = ref(null);
const isLoading = ref(false);

const forgotForm = reactive({ email: "" });

const forgotRules = {
  email: [
    { required: true, message: "请输入邮箱地址", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: ["blur", "change"] }
  ],
};

const handleSubmit = () => {
  if (!forgotFormRef.value) {
    ElMessage.error("表单未初始化");
    return;
  }
  forgotFormRef.value.validate(async (valid) => {
    if (valid) {
      isLoading.value = true;
      try {
        const res = await forgotPassword({ email: forgotForm.email });
        ElMessage.success(res.message || "重置链接已发送至您的邮箱");
      } catch (error) {
        if (error.response) {
          ElMessage.error(error.response.data?.message || "请求失败");
        } else {
          ElMessage.error("网络错误，请稍后重试");
        }
      } finally {
        isLoading.value = false;
      }
    } else {
      ElMessage.warning("邮箱格式不正确");
    }
  });
};
</script>

<style scoped>
/* 修复背景铺满全屏 */
.forgot-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: url('./background/2.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* 遮罩层 */
.forgot-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.35);
  z-index: 1;
}

/* 装饰符号 */
.forgot-container::after {
  content: "🌾🌱🍃";
  position: absolute;
  bottom: 3%;
  right: 2%;
  font-size: 140px;
  opacity: 0.15;
  pointer-events: none;
  z-index: 1;
}

/* 卡片样式 */
.forgot-card {
  position: relative;
  z-index: 2;
  width: 90%;
  max-width: 500px;
  background: rgba(255, 250, 240, 0.85);
  backdrop-filter: blur(12px);
  border-radius: 40px;
  padding: 52px 44px;
  box-shadow: 0 30px 50px -20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 245, 215, 0.6);
  transition: transform 0.3s;
}
.forgot-card:hover {
  transform: scale(1.01);
}

.card-inner {
  display: flex;
  flex-direction: column;
}

.brand {
  text-align: center;
  margin-bottom: 40px;
}
.logo-icon {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #1A3A32 0%, #2B5A48 100%);
  border-radius: 50%;
  margin: 0 auto 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 30px -10px rgba(0,0,0,0.3), inset 0 2px 4px rgba(255,255,255,0.3);
  border: 2px solid rgba(207, 181, 59, 0.5);
}
.title {
  font-family: Georgia, "Times New Roman", "PingFang SC", "Microsoft YaHei", serif;
  font-size: 36px;
  font-weight: 600;
  line-height: 1.4;
  background: linear-gradient(135deg, #1A3A32 0%, #3B6B58 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 6px;
}
.subtitle {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 14px;
  color: #A08C5E;
  margin-top: 8px;
}

/* 输入框样式 */
.custom-input :deep(.el-input__wrapper) {
  background-color: rgba(254, 249, 240, 0.9);
  border-radius: 20px;
  border: 1px solid #E5DAC8;
  transition: all 0.2s;
  padding: 4px 16px;
}
.custom-input :deep(.el-input__wrapper:hover) {
  border-color: #CFB53B;
}
.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #1A3A32;
  box-shadow: 0 0 0 3px rgba(26,58,50,0.1);
}

/* 按钮样式 */
.submit-btn {
  width: 100%;
  height: 56px;
  border-radius: 40px;
  font-size: 17px;
  font-weight: 600;
  background: linear-gradient(135deg, #1A3A32 0%, #2B5A48 100%);
  border: none;
  margin-top: 8px;
  transition: all 0.3s;
}
.submit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px -10px rgba(26,58,50,0.5);
}

.back-prompt {
  text-align: center;
  margin-top: 32px;
}
.back-link {
  font-size: 14px;
  color: #A08C5E;
  text-decoration: none;
}
.back-link:hover {
  color: #1A3A32;
}
</style>