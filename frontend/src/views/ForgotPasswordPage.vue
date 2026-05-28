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
            v-model.trim="forgotForm.email"
            type="email"
            placeholder="请输入您的注册邮箱"
            size="large"
            clearable
            @keyup.enter="handleSubmit"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
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

const handleSubmit = async () => {
  // 🌟 终极调试：如果这都不弹窗，说明按钮没点上
  window.alert("点到了按钮！正在处理...");
  
  // 1. 立即打印日志
  console.log("🔥 [DEBUG] 找回密码按钮被点击了！输入内容:", forgotForm.email);
  
  // 2. 基本非空校验（跳过复杂的 validate 提高成功率）
  if (!forgotForm.email || !forgotForm.email.includes('@')) {
    console.warn("⚠️ [DEBUG] 邮箱格式看起来不对:", forgotForm.email);
    ElMessage.warning("请输入有效的邮箱地址！");
    return;
  }

  console.log("🚀 [DEBUG] 校验通过，准备发起网络请求...");
  isLoading.value = true;
  
  try {
    // 3. 发起请求
    const res = await forgotPassword({ email: forgotForm.email });
    console.log("✅ [DEBUG] 后端响应成功:", res);
    
    // 兼容不同的后端返回格式
    const isSuccess = res.code === 200 || res.success === true;
    
    if (isSuccess) {
      ElMessage.success(res.message || "重置链接已发送，请查收您的邮箱！");
    } else {
      console.warn("🧐 [DEBUG] 后端返回了非成功状态码:", res);
      ElMessage.warning(res.message || "发送失败，请检查邮箱是否已注册");
    }
  } catch (error) {
    console.error("❌ [DEBUG] 网络请求发生灾难性错误:", error);
    
    let errorDetail = "未知错误";
    if (error.response) {
      errorDetail = `后端报错 (${error.response.status}): ${JSON.stringify(error.response.data)}`;
    } else if (error.request) {
      errorDetail = "请求已发出但未收到响应，请检查后端 8000 端口是否存活";
    } else {
      errorDetail = error.message;
    }
    
    ElMessage.error("发送失败：" + errorDetail);
  } finally {
    isLoading.value = false;
    console.log("🏁 [DEBUG] 请求流程结束。");
  }
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