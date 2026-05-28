<template>
  <div class="forgot-container">
    <div class="forgot-card">
      <div class="forgot-header">
        <div class="logo-icon">
          <el-icon :size="40" color="#27ae60"><Lock /></el-icon>
        </div>
        <h1 class="forgot-title">找回密码</h1>
        <p class="forgot-subtitle">输入您的注册邮箱，我们将发送重置链接</p>
      </div>

      <el-form
        ref="forgotFormRef"
        :model="forgotForm"
        :rules="forgotRules"
        class="forgot-form"
      >
        <el-form-item prop="email">
          <el-input
            v-model="forgotForm.email"
            type="email"
            placeholder="请输入您的注册邮箱"
            size="large"
            prefix-icon="Message"
            @keyup.enter="handleSubmit"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" class="submit-btn" :loading="isLoading" @click="handleSubmit">
            发送重置链接
          </el-button>
        </el-form-item>
      </el-form>

      <div class="back-link">
        <span>想起密码了？</span>
        <router-link to="/login">返回登录</router-link>
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
const isLoading = ref(false); // 增加 loading 状态

const forgotForm = reactive({
  email: "",
});

// 🌟 恢复邮箱格式校验
const forgotRules = {
  email: [
    { required: true, message: "请输入邮箱地址", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: ["blur", "change"] }
  ],
};

const handleSubmit = () => {
  // 1. 强制在控制台留痕，只要点了按钮这行必出
  console.log("👉 按钮点击事件被成功触发了！");

  if (!forgotFormRef.value) {
    ElMessage.error("前端错误：表单 ref 绑定失败，组件未加载完毕！");
    return;
  }

  forgotFormRef.value.validate(async (valid) => {
    if (valid) {
      isLoading.value = true; // 开始加载
      try {
        console.log("🚀 前端格式校验通过！准备向后端发送数据:", forgotForm.email);

        // 调用你的 auth.js 接口
        const res = await forgotPassword({ email: forgotForm.email });

        console.log("📦 后端成功响应了:", res);
        ElMessage.success(res.message || "重置链接已发送到您的邮箱，请去后端查看！");

      } catch (error) {
        // 🌟 重点抓取：把隐藏的网络错误直接通过弹窗逼出来！
        console.error("🚨 网络请求彻底失败，详细错误信息如下:", error);

        // 如果后端有响应（比如返回了 400 提示邮箱未注册）
        if (error.response) {
          const apiMessage = error.response.data?.message || error.response.data?.detail || "后端拒绝了请求";
          ElMessage.error(`后端报错 (${error.response.status}): ${apiMessage}`);
        } else {
          // 如果连响应都没有（比如跨域失败、或者 8000 端口压根连不上）
          ElMessage.error("网络连接失败或超时！请检查后端配置或控制台报错。");
        }
      } finally {
        isLoading.value = false; // 结束加载
      }
    } else {
      console.warn("⚠️ 邮箱格式验证未通过，被 Element 拦截");
      // 🌟 必须加上这一行，用户点击没反应时才会弹出提示
      ElMessage.warning("邮箱格式不正确，请检查输入的邮箱地址！");
    }
  });
};
</script>

<style scoped>
.forgot-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); }
.forgot-card { width: 100%; max-width: 400px; padding: 40px; background: #ffffff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); }
.forgot-header { text-align: center; margin-bottom: 32px; }
.logo-icon { width: 60px; height: 60px; margin: 0 auto 16px; background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.forgot-title { font-size: 22px; font-weight: 600; color: #1f2937; margin-bottom: 6px; }
.forgot-subtitle { font-size: 13px; color: #6b7280; }
.forgot-form { margin-bottom: 24px; }
.submit-btn { width: 100%; height: 44px; border-radius: 8px; font-size: 15px; font-weight: 500; }
.back-link { text-align: center; font-size: 13px; color: #6b7280; }
.back-link a { color: #27ae60; margin-left: 4px; }
.back-link a:hover { text-decoration: underline; }
</style>