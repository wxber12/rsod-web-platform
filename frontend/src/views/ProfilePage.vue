<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">个人中心</h1>
      <p class="page-subtitle">管理您的账户信息和使用统计</p>
    </div>

    <div class="profile-content" v-loading="loading">
      <div class="user-info-card">
        <div class="user-avatar-section">
          <el-avatar :size="80" :src="userInfo.avatar || defaultAvatar" />
          <div class="user-basic-info">
            <div class="user-name">{{ userInfo.username || '加载中...' }}</div>
            <div class="user-role">{{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}</div>
            <div class="user-email" v-if="userInfo.email">
              <el-icon><Message /></el-icon> {{ userInfo.email }}
            </div>
            <div class="action-buttons">
              <el-button size="small" type="primary" plain @click="editProfileVisible = true">
                编辑资料
              </el-button>
              <el-button size="small" type="warning" plain @click="changePasswordVisible = true">
                修改密码
              </el-button>
              <el-button size="small" type="danger" plain @click="handleLogout">
                退出登录
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_detections }}</div>
          <div class="stat-label">总检测次数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_objects }}</div>
          <div class="stat-label">累计检测病虫害</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.success_rate }}%</div>
          <div class="stat-label">检测成功率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.usage_days }}</div>
          <div class="stat-label">使用天数</div>
        </div>
      </div>
    </div>

    <!-- 编辑资料对话框 -->
    <el-dialog v-model="editProfileVisible" title="编辑个人资料" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="userInfo.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入新邮箱" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editProfileVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateProfile" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="changePasswordVisible" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="100px" :rules="passwordRules" ref="passwordFormRef">
        <el-form-item label="当前密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePasswordVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="submitting">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// 脚本部分完全保留原逻辑，不做任何修改
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { Message } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '../utils/request';

const router = useRouter();
const loading = ref(false);
const submitting = ref(false);
const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png';

const userInfo = ref({
  username: '',
  role: '',
  email: '',
  avatar: ''
});

const stats = ref({
  total_detections: 0,
  total_objects: 0,
  success_rate: 100,
  usage_days: 1
});

const editProfileVisible = ref(false);
const editForm = reactive({
  email: ''
});

const changePasswordVisible = ref(false);
const passwordFormRef = ref(null);
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
});

const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入密码不一致'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

const fetchProfile = async () => {
  loading.value = true;
  try {
    const res = await request.get('/profile/');
    userInfo.value = res;
    editForm.email = res.email;

    const historyRes = await request.get('/history/', { params: { limit: 1000 } });
    if (historyRes.success) {
      stats.value.total_detections = historyRes.data.length;
      stats.value.total_objects = historyRes.data.reduce((acc, curr) => acc + (curr.total_objects || 0), 0);

      if (historyRes.data.length > 0) {
        const firstDate = new Date(historyRes.data[historyRes.data.length - 1].created_at);
        const diffTime = Math.abs(new Date() - firstDate);
        stats.value.usage_days = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) || 1;
      }
    }
  } catch (error) {
    ElMessage.error('获取个人资料失败');
  } finally {
    loading.value = false;
  }
};

const handleUpdateProfile = async () => {
  submitting.value = true;
  try {
    await request.put('/profile/', { email: editForm.email });
    ElMessage.success('资料更新成功');
    editProfileVisible.value = false;
    fetchProfile();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '更新失败');
  } finally {
    submitting.value = false;
  }
};

const handleChangePassword = async () => {
  await passwordFormRef.value.validate();
  submitting.value = true;
  try {
    await request.post('/profile/change-password', {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    });
    ElMessage.success('密码修改成功，请重新登录');
    changePasswordVisible.value = false;
    // 自动触发退出登录
    handleLogout();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '修改失败');
  } finally {
    submitting.value = false;
  }
};

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出当前账号并切换吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    router.push('/login');
    ElMessage.success('已退出登录');
  }).catch(() => {});
};

onMounted(() => {
  fetchProfile();
});
</script>

<style scoped>
/* 农业主题统一样式（与 LoginPage1.0 保持一致） */
.profile-page {
  min-height: 100vh;
  padding: 32px 48px;
  background-image: url('./background/2.jpg');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
}

.profile-page::before {
  content: "";
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.08);
  pointer-events: none;
  z-index: 0;
}

.page-header {
  position: relative;
  z-index: 2;
  margin-bottom: 32px;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(6px);
  border-radius: 24px;
  padding: 28px 32px;
}

.page-title {
  font-size: 42px;
  font-weight: 800;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  margin-bottom: 12px;
  letter-spacing: 2px;
}

.page-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 240, 0.9);
  letter-spacing: 1px;
}

.profile-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.user-info-card {
  background: rgba(255, 252, 245, 0.88);
  backdrop-filter: blur(16px);
  border-radius: 48px;
  padding: 40px;
  border: 1px solid rgba(255, 245, 215, 0.6);
}

.user-avatar-section {
  display: flex;
  align-items: center;
  gap: 32px;
  flex-wrap: wrap;
}

.user-basic-info {
  flex: 1;
}

.user-name {
  font-size: 32px;
  font-weight: 800;
  color: #1a3a32;
  margin-bottom: 8px;
}

.user-role {
  font-size: 16px;
  color: #5d6e4a;
  margin-bottom: 8px;
  background: rgba(207, 181, 59, 0.2);
  display: inline-block;
  padding: 4px 16px;
  border-radius: 40px;
}

.user-email {
  font-size: 16px;
  color: #5d6e4a;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  border-radius: 40px;
  padding: 8px 24px;
  font-weight: 500;
  transition: all 0.2s;
}

.action-buttons .el-button--primary.is-plain {
  background: rgba(46, 125, 50, 0.15);
  border-color: #2e7d32;
  color: #1a3a32;
}

.action-buttons .el-button--primary.is-plain:hover {
  background: #2e7d32;
  color: white;
}

.action-buttons .el-button--warning.is-plain {
  background: rgba(207, 181, 59, 0.15);
  border-color: #cfb53b;
  color: #1a3a32;
}

.action-buttons .el-button--warning.is-plain:hover {
  background: #cfb53b;
  color: white;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 28px;
}

.stat-card {
  background: rgba(255, 252, 245, 0.88);
  backdrop-filter: blur(16px);
  border-radius: 36px;
  padding: 36px 24px;
  text-align: center;
  border: 1px solid rgba(255, 245, 215, 0.6);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-6px);
  background: rgba(255, 252, 245, 0.96);
}

.stat-value {
  font-size: 48px;
  font-weight: 800;
  color: #2e7d32;
  margin-bottom: 12px;
}

.stat-label {
  font-size: 18px;
  color: #5d6e4a;
  font-weight: 500;
}

/* 弹窗样式覆盖，保持一致性 */
:deep(.el-dialog) {
  border-radius: 32px;
  background: rgba(255, 252, 245, 0.96);
  backdrop-filter: blur(8px);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  margin-right: 0;
}

:deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: 700;
  color: #1a3a32;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-form-item__label) {
  color: #5d6e4a;
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  background-color: rgba(254, 249, 240, 0.9);
  border-radius: 20px;
  border: 1px solid #E5DAC8;
  transition: all 0.2s;
}

:deep(.el-input__wrapper:hover) {
  border-color: #CFB53B;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #1A3A32;
  box-shadow: 0 0 0 3px rgba(26, 58, 50, 0.1);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #1a3a32, #2b5a48);
  border: none;
  border-radius: 40px;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(26, 58, 50, 0.3);
}

@media (max-width: 768px) {
  .profile-page {
    padding: 24px 24px;
  }
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
  .stat-value {
    font-size: 36px;
  }
  .stat-label {
    font-size: 16px;
  }
  .user-avatar-section {
    flex-direction: column;
    text-align: center;
  }
  .user-basic-info {
    margin-left: 0;
  }
}
</style>