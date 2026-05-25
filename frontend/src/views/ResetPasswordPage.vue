<template>
  <div class="reset-container">
    <div class="reset-card">
      <div class="reset-header">
        <h1 class="reset-title">设置新密码</h1>
        <p class="reset-subtitle">请输入您要修改的新密码</p>
      </div>

      <el-form ref="resetFormRef" :model="resetForm" :rules="resetRules" class="reset-form">
        <el-form-item prop="password">
          <el-input
            v-model="resetForm.password"
            type="password"
            placeholder="请输入新密码(至少6位)"
            show-password
            size="large"
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
            @keyup.enter="handleReset"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" class="submit-btn" @click="handleReset">
            确认修改密码
          </el-button>
        </el-form-item>
      </el-form>
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

const resetForm = reactive({
  password: "",
  confirmPassword: "",
  token: ""
});

// 获取 URL 传过来的 ?token=xxxx
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
      }
    }
  });
};
</script>

<style scoped>
/* 样式可以直接复用你 ForgotPasswordPage.vue 的布局样式 */
.reset-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); }
.reset-card { width: 100%; max-width: 400px; padding: 40px; background: #ffffff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
.reset-header { text-align: center; margin-bottom: 32px; }
.reset-title { font-size: 22px; font-weight: 600; color: #1f2937; margin-bottom: 6px; }
.reset-subtitle { font-size: 13px; color: #6b7280; }
.submit-btn { width: 100%; height: 44px; border-radius: 8px; }
</style>