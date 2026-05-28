<template>
  <div class="reset-container">
    <div class="reset-card">
      <div class="card-inner">
        <div class="brand">
          <div class="logo-icon">
            <el-icon :size="56" color="#CFB53B"><Lock /></el-icon>
          </div>
          <h1 class="title">设置新密码</h1>
          <p class="subtitle">请输入您要修改的新密码</p>
        </div>

        <el-form ref="resetFormRef" :model="resetForm" :rules="resetRules" class="reset-form">
          <el-form-item prop="password">
            <el-input
              v-model="resetForm.password"
              type="password"
              placeholder="请输入新密码(至少6位)"
              show-password
              size="large"
              class="custom-input"
              @keyup.enter="handleReset"
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="resetForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              show-password
              size="large"
              class="custom-input"
              @keyup.enter="handleReset"
            />
          </el-form-item>

          <el-button type="primary" size="large" class="submit-btn" :loading="submitting" @click="handleReset">
            确认修改密码
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
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { resetPassword } from "../api/auth";

const route = useRoute();
const router = useRouter();
const resetFormRef = ref(null);
const submitting = ref(false); // 添加 loading 状态（可选，提升用户体验）

const resetForm = reactive({
  password: "",
  confirmPassword: "",
  token: ""
});

onMounted(() => {
  if (route.query.token) {
    resetForm.token = route.query.token;
  } else {
    ElMessage.error("链接缺少凭证，无法重置密码！");
    router.push("/login");
  }
});

const validateConfirm = (rule, value, callback) => {
  if (value !== resetForm.password) {
    callback(new Error("两次输入的密码不一致！"));
  } else {
    callback();
  }
};

const resetRules = {
  password: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 6, message: "密码长度至少为 6 位", trigger: "blur" }
  ],
  confirmPassword: [
    { required: true, message: "请再次输入密码", trigger: "blur" },
    { validator: validateConfirm, trigger: "blur" }
  ]
};

const handleReset = () => {
  resetFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        await resetPassword({
          token: resetForm.token,
          new_password: resetForm.password
        });
        ElMessage.success("密码修改成功，正在跳转登录页...");
        setTimeout(() => {
          router.push("/login");
        }, 2000);
      } catch (error) {
        ElMessage.error(error.response?.data?.message || "重置失败，链接可能已过期");
      } finally {
        submitting.value = false;
      }
    }
  });
};
</script>

<style scoped>
/* 农业主题统一样式（与 LoginPage1.0 保持一致） */
.reset-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-image: url('./background/2.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}

.reset-container::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 1;
}

.reset-container::after {
  content: "🌾🌱🍃";
  position: absolute;
  bottom: 5%;
  right: 3%;
  font-size: 140px;
  opacity: 0.15;
  pointer-events: none;
  z-index: 1;
}

.reset-card {
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

.reset-card:hover {
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

.reset-form {
  margin-bottom: 20px;
}

.custom-input :deep(.el-input__wrapper) {
  background-color: rgba(254, 249, 240, 0.9);
  border-radius: 20px;
  border: 1px solid #E5DAC8;
  transition: all 0.2s;
  padding: 4px 16px;
}

.custom-input :deep(.el-input__wrapper:hover) {
  border-color: #CFB53B;
  background-color: rgba(254, 249, 240, 1);
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #1A3A32;
  box-shadow: 0 0 0 3px rgba(26, 58, 50, 0.1);
}

.submit-btn {
  width: 100%;
  height: 56px;
  border-radius: 40px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 17px;
  font-weight: 600;
  background: linear-gradient(135deg, #1A3A32 0%, #2B5A48 100%);
  border: none;
  margin-top: 8px;
  letter-spacing: 1px;
  transition: all 0.3s;
}

.submit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px -10px rgba(26, 58, 50, 0.5);
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