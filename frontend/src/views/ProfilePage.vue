<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">个人中心</h1>
      <p class="page-subtitle">管理你的账户信息和使用统计</p>
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
          <div class="stat-label">累计检测目标</div>
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
    
    // 获取统计信息 (从历史记录接口简单估算或新增统计接口)
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

<style scoped lang="scss">
.profile-page {
  width: 100%;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 32px;

    .page-title {
      font-size: 28px;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 8px;
    }

    .page-subtitle {
      font-size: 16px;
      color: #6b7280;
    }
  }

  .profile-content {
    display: flex;
    flex-direction: column;
    gap: 32px;

    .user-info-card {
      background: white;
      border-radius: 12px;
      padding: 32px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      border: 1px solid #e5e7eb;

      .user-avatar-section {
        display: flex;
        align-items: center;

        .user-basic-info {
          margin-left: 32px;

          .user-name {
            font-size: 26px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 4px;
          }

          .user-role {
            font-size: 14px;
            color: #4f46e5;
            font-weight: 600;
            background: #eef2ff;
            padding: 2px 10px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 8px;
          }

          .user-email {
            font-size: 14px;
            color: #6b7280;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 16px;
          }

          .action-buttons {
            display: flex;
            gap: 12px;
          }
        }
      }
    }

    .stats-cards {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 24px;

      .stat-card {
        background: white;
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        transition: transform 0.2s;

        &:hover {
          transform: translateY(-4px);
        }

        .stat-value {
          font-size: 36px;
          font-weight: 800;
          color: #4f46e5;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #6b7280;
          font-weight: 500;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .profile-content {
    .stats-cards {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}
</style>
