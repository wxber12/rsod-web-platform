<template>
  <div class="register-container">
    <div class="register-card">
      <div class="card-inner">
        <div class="brand">
          <div class="logo-icon">
            <el-icon :size="56" color="#CFB53B"><UserFilled /></el-icon>
          </div>
          <h1 class="title">创建账号</h1>
          <p class="subtitle">开启智慧农业之旅</p>
        </div>

        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="register-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="用户名"
              size="large"
              class="custom-input"
              @keyup.enter="handleRegister"
            >
              <template #prefix><el-icon><User /></el-icon></template>
            </el-input>
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              type="email"
              placeholder="邮箱"
              size="large"
              class="custom-input"
              @keyup.enter="handleRegister"
            >
              <template #prefix><el-icon><Message /></el-icon></template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="密码"
              size="large"
              class="custom-input"
              @keyup.enter="handleRegister"
            >
              <template #prefix><el-icon><Lock /></el-icon></template>
            </el-input>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="确认密码"
              size="large"
              class="custom-input"
              @keyup.enter="handleRegister"
            >
              <template #prefix><el-icon><Lock /></el-icon></template>
            </el-input>
          </el-form-item>

          <div class="agree-terms">
            <el-checkbox v-model="registerForm.agree" class="agree-check"/>
            <span>我已阅读并同意</span>
            <a href="#" class="terms-link">《服务协议》</a>
            <span>与</span>
            <a href="#" class="terms-link">《隐私政策》</a>
          </div>

          <el-button type="primary" size="large" class="register-btn" :loading="loading" @click="handleRegister">
            注册
          </el-button>
        </el-form>

        <div class="login-prompt">
          <span>已有账号？</span>
          <router-link to="/login" class="login-link">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { UserFilled, User, Message, Lock } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { register } from "../api/auth";

const router = useRouter();
const loading = ref(false);
const registerFormRef = ref(null);

const registerForm = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  agree: false,
});

const registerRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度在3到20个字符", trigger: "blur" },
    { pattern: /^[a-zA-Z0-9_]+$/, message: "用户名只能包含字母、数字和下划线", trigger: "blur" },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度在6到30个字符", trigger: "blur" },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: "密码需包含字母和数字", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认密码", trigger: "blur" },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error("两次输入的密码不一致"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
};

const handleRegister = () => {
  if (!registerForm.agree) {
    ElMessage.warning("请先阅读并勾选同意服务条款和隐私政策！");
    return;
  }

  registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await register({
          username: registerForm.username,
          password: registerForm.password,
          email: registerForm.email
        });

        if (res.code === 200 || (res.data && res.data.code === 200)) {
          const responseData = res.code === 200 ? res : res.data;
          ElMessage.success(responseData.message || "注册成功！即将为您跳转到登录页...");
          setTimeout(() => {
            router.push("/login");
          }, 1500);
        } else {
          const errorMsg = res.message || res.data?.message || "注册失败";
          ElMessage.error(errorMsg);
        }
      } catch (error) {
        console.error("注册网络对接异常:", error);
        if (error.response && error.response.data) {
          ElMessage.error(error.response.data.message || "注册申请被拒绝");
        } else {
          ElMessage.error("无法连接到后端服务器，请确认 FastAPI 容器已启动！");
        }
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-image: url('./background/2.jpg');
  background-size: cover;
  background-position: center center;
  background-attachment: fixed;
  background-color: #1A2A24;
}

.register-container::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 1;
}

.register-container::after {
  content: "🌾🌱🍃";
  position: absolute;
  bottom: 5%;
  left: 3%;
  font-size: 140px;
  opacity: 0.2;
  font-family: system-ui;
  pointer-events: none;
  z-index: 1;
}

.register-card {
  width: 90%;
  max-width: 560px;
  background: rgba(255, 250, 240, 0.78);
  backdrop-filter: blur(12px);
  border-radius: 40px;
  padding: 48px 48px;
  box-shadow: 0 30px 50px -20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 245, 215, 0.6);
  z-index: 2;
  transition: transform 0.3s ease;
}
.register-card:hover {
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
  margin: 0 auto 24px;
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
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #1A3A32 0%, #3B6B58 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 6px;
}
.subtitle {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  letter-spacing: 1.5px;
  color: #A08C5E;
  text-transform: uppercase;
  font-weight: 500;
  text-shadow: 0 1px 1px rgba(255,255,255,0.3);
}

.register-form {
  margin-bottom: 20px;
}
.custom-input :deep(.el-input__wrapper) {
  background-color: rgba(254, 249, 240, 0.9);
  border-radius: 20px;
  box-shadow: none;
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
.custom-input :deep(.el-input__inner) {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 15px;
}

.agree-terms {
  display: flex;
  align-items: center;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 12px;
  color: #2C3E2B;
  margin: 16px 0 24px;
  gap: 4px;
  flex-wrap: wrap;
}
.terms-link {
  color: #CFB53B;
  text-decoration: none;
}
.terms-link:hover {
  color: #1A3A32;
}

.register-btn {
  width: 100%;
  height: 56px;
  border-radius: 40px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 17px;
  font-weight: 600;
  background: linear-gradient(135deg, #1A3A32 0%, #2B5A48 100%);
  border: none;
  letter-spacing: 1px;
  transition: all 0.3s;
}
.register-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px -10px rgba(26, 58, 50, 0.5);
  background: linear-gradient(135deg, #2B5A48 0%, #1A3A32 100%);
}

.login-prompt {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(235, 227, 213, 0.6);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 14px;
  color: #2C3E2B;
}
.login-link {
  color: #1A3A32;
  font-weight: 600;
  text-decoration: none;
  margin-left: 6px;
}
.login-link:hover {
  color: #CFB53B;
}
</style>