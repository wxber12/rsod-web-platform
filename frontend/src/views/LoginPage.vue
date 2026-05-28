<template>
  <div class="login-container">
    <div class="login-card">
      <div class="card-inner">
        <div class="brand">
          <div class="logo-icon">
            <el-icon :size="56" color="#CFB53B"><Crop /></el-icon>
          </div>
          <h1 class="title">农业病虫害智能识别系统</h1>
          <p class="subtitle">Agricultural Pest Intelligence</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名 / 手机号"
              size="large"
              class="custom-input"
              @keyup.enter="handleLogin"
            >
              <template #prefix><el-icon><User /></el-icon></template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              size="large"
              class="custom-input"
              @keyup.enter="handleLogin"
            >
              <template #prefix><el-icon><Lock /></el-icon></template>
            </el-input>
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="loginForm.remember" class="remember-check">记住账号</el-checkbox>
            <router-link to="/forgot-password" class="forgot-link">忘记密码?</router-link>
          </div>

          <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
            登录
          </el-button>
        </el-form>

        <div class="register-prompt">
          <span>尚未注册？</span>
          <router-link to="/register" class="register-link">立即创建账号</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { Crop, User, Lock } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { login } from "../api/auth";

const router = useRouter();
const loading = ref(false);

const loginForm = reactive({
  username: "",
  password: "",
  remember: false,
});

const loginRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度在3到20个字符", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度在6到30个字符", trigger: "blur" },
  ],
};

const loginFormRef = ref(null);

const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await login({
          username: loginForm.username,
          password: loginForm.password
        });

        console.log("前端接收到的登录响应数据：", res);

        if (res.code === 200 || (res.data && res.data.code === 200)) {
          const responseData = res.code === 200 ? res : res.data;
          ElMessage.success(responseData.message || "登录成功，欢迎回来！");
          const token = responseData.data.token;
          localStorage.setItem("token", token);
          router.push("/detection");
        } else {
          const errorMsg = res.message || res.data?.message || "用户名或密码错误";
          ElMessage.error(errorMsg);
        }
      } catch (error) {
        console.error("登录对接异常:", error);
        if (error.response && error.response.data) {
          ElMessage.error(error.response.data.message || "登录验证失败");
        } else {
          ElMessage.error("未能连接到后端服务，请确认 FastAPI 后端和 Docker 数据库均已开启！");
        }
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-image: url('./background/2.jpg');
  background-size: cover;
  background-position: center center;
  background-attachment: fixed;
}

.login-container::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.login-container::after {
  content: "🌾🌱🍃";
  position: absolute;
  bottom: 5%;
  right: 3%;
  font-size: 140px;
  opacity: 0.15;
  font-family: system-ui;
  pointer-events: none;
  white-space: pre;
  z-index: 1;
}

.login-card {
  width: 90%;
  max-width: 560px;
  background: rgba(255, 250, 240, 0.75);
  backdrop-filter: blur(12px);
  border-radius: 40px;
  padding: 52px 48px;
  box-shadow: 0 30px 50px -20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 245, 215, 0.6);
  z-index: 2;
  transition: transform 0.3s ease;
}
.login-card:hover {
  transform: scale(1.01);
}

.card-inner {
  display: flex;
  flex-direction: column;
}

.brand {
  text-align: center;
  margin-bottom: 48px;
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
  font-size: 38px;
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

.login-form {
  margin-bottom: 28px;
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0 32px;
}
.remember-check :deep(.el-checkbox__label) {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 13px;
  color: #2C3E2B;
}
.forgot-link {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 13px;
  color: #CFB53B;
  text-decoration: none;
  font-weight: 500;
  text-shadow: 0 0 2px rgba(0,0,0,0.1);
}
.forgot-link:hover {
  color: #1A3A32;
}

.login-btn {
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
.login-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px -10px rgba(26, 58, 50, 0.5);
  background: linear-gradient(135deg, #2B5A48 0%, #1A3A32 100%);
}

.register-prompt {
  text-align: center;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 14px;
  color: #2C3E2B;
  padding-top: 20px;
  border-top: 1px solid rgba(235, 227, 213, 0.6);
}
.register-link {
  color: #1A3A32;
  font-weight: 600;
  text-decoration: none;
  margin-left: 6px;
}
.register-link:hover {
  color: #CFB53B;
}
</style>