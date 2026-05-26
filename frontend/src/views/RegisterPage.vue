<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <div class="logo-icon">
          <el-icon :size="40" color="#27ae60"><UserFilled /></el-icon>
        </div>
        <h1 class="register-title">创建账号</h1>
        <p class="register-subtitle">加入我们，开始智能检测之旅</p>
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
            placeholder="请输入用户名"
            size="large"
            @keyup.enter="handleRegister"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            type="email"
            placeholder="请输入邮箱"
            size="large"
            @keyup.enter="handleRegister"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            @keyup.enter="handleRegister"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            size="large"
            @keyup.enter="handleRegister"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item class="agree-terms">
          <el-checkbox v-model="registerForm.agree" />
          <span>我已阅读并同意</span>
          <a href="#" class="terms-link">《服务条款》</a>
          <span>和</span>
          <a href="#" class="terms-link">《隐私政策》</a>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" class="register-btn" @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-link">
        <span>已有账号？</span>
        <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { UserFilled, User, Message, Lock } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus"; // 🌟 引入弹窗提示
import { register } from "../api/auth";    // 🌟 引入刚刚编写的真实注册 API

const router = useRouter();
const loading = ref(false); // 🌟 注册按钮的加载控制动画
const registerFormRef = ref(null);

const registerForm = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  agree: false,
});

// 你原本写的非常严谨完善的表单校验规则，保持不变
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

// 🌟 升级为真实的 async/await 注册对接逻辑
const handleRegister = () => {
  // 1. 优先检查是否勾选了同意协议 (弹窗提醒)
  if (!registerForm.agree) {
    ElMessage.warning("请先阅读并勾选同意服务条款和隐私政策！");
    return;
  }

  registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        // 向 FastAPI 发送注册数据，只剥离出后端需要的字段
        const res = await register({
          username: registerForm.username,
          password: registerForm.password,
          email: registerForm.email // 🌟 将邮箱字段发送给后端
        });

        // 兼容 request.js 拦截器剥皮与不剥皮格式
        if (res.code === 200 || (res.data && res.data.code === 200)) {
          const responseData = res.code === 200 ? res : res.data;

          ElMessage.success(responseData.message || "注册成功！即将为您跳转到登录页...");

          // 优雅等待 1.5 秒，让用户看清成功提示后，自动路由切回登录页面
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
        loading.value = false; // 解冻按钮状态
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
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}

.register-card {
  width: 100%;
  max-width: 420px;
  padding: 40px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.register-header {
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

.register-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 6px;
}

.register-subtitle {
  font-size: 13px;
  color: #6b7280;
}

.register-form {
  margin-bottom: 24px;
}

.agree-terms {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 16px;
}

.terms-link {
  color: #27ae60;
  margin: 0 4px;
}

.terms-link:hover {
  text-decoration: underline;
}

.register-btn {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
}

.login-link {
  text-align: center;
  font-size: 13px;
  color: #6b7280;
}

.login-link a {
  color: #27ae60;
  margin-left: 4px;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>