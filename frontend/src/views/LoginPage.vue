<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="40" color="#ffffff"><Picture /></el-icon>
        </div>
        <h1 class="login-title">遥感目标智能检测平台</h1>
        <p class="login-subtitle">多场景遥感影像 · 精准目标检测</p>
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
            placeholder="请输入用户名"
            size="large"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item class="form-actions">
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          <router-link to="/forgot-password" class="forgot-password">忘记密码?</router-link>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-link">
        <span>还没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { Picture, User, Lock } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus"; // 引入 ElementPlus 弹窗提示组件
import { login } from "../api/auth";        // 引入真实 API 接口

const router = useRouter();
const loading = ref(false); // 登录状态控制

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

// 核心登录逻辑
const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        // 1. 只把后端需要的账号密码剥离出来丢给接口
        const res = await login({
          username: loginForm.username,
          password: loginForm.password
        });

        console.log("前端接收到的登录响应数据：", res);

        // 2. 全兼容判断：无论你的 request.js 拦截器剥皮了没有，只要有一层拿到 code===200 就放行
        if (res.code === 200 || (res.data && res.data.code === 200)) {

          // 根据剥包状态自动获取正确的数据源
          const responseData = res.code === 200 ? res : res.data;

          // 弹出温暖快乐的登录成功小浮窗
          ElMessage.success(responseData.message || "登录成功，欢迎回来！");

          // 3. 稳妥取出那一长串身份令牌 token，保存到浏览器的本地存储中
          const token = responseData.data.token;
          localStorage.setItem("token", token);

          // 4. 破门而入，直接跳转至遥感大厅
          router.push("/detection");
        } else {
          // 接收到后端返回的 400 账号错误提示等数据包
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
        loading.value = false; // 解冻按钮状态
      }
    }
  });
};
</script>

<style scoped>
/* 保持原本非常优雅漂亮的 UI 绿色渐变样式 */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}
.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.logo-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 6px;
}
.login-subtitle {
  font-size: 13px;
  color: #6b7280;
}
.login-form {
  margin-bottom: 24px;
}
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
:deep(.el-form-item__content) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.forgot-password {
  font-size: 13px;
  color: #27ae60;
  cursor: pointer;
  text-decoration: none;
}
.forgot-password:hover {
  text-decoration: underline;
}
.login-btn {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  border: none;
}
.login-btn:hover {
  background: linear-gradient(135deg, #219653 0%, #27ae60 100%);
  opacity: 0.9;
}
.register-link {
  text-align: center;
  font-size: 13px;
  color: #6b7280;
}
.register-link a {
  color: #27ae60;
  margin-left: 4px;
  cursor: pointer;
  text-decoration: none;
}
.register-link a:hover {
  text-decoration: underline;
}
</style>