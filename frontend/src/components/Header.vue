<template>
  <div class="header-container">
    <div class="breadcrumbs">
      <el-icon class="breadcrumb-icon"><House /></el-icon>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-text">智能检测</span>
    </div>

    <div class="header-actions">
      <div class="action-icons">
        <el-icon class="action-icon"><Grid /></el-icon>
        <el-icon class="action-icon"><Bell /></el-icon>
        <el-icon class="action-icon"><QuestionFilled /></el-icon>
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="user-dropdown">
            <el-avatar class="user-avatar" :size="32">
              <img
                :src="userInfo.avatar || defaultAvatar"
                alt="用户头像"
              />
            </el-avatar>
            <div class="user-info">
              <div class="user-name">{{ userInfo.username || 'Lily' }}</div>
              <div class="user-role">{{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}</div>
            </div>
            <el-icon class="dropdown-icon"><CaretBottom /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import {
  Grid,
  Bell,
  QuestionFilled,
  CaretBottom,
  House,
} from "@element-plus/icons-vue";
import { ElMessageBox, ElMessage } from 'element-plus';
import request from '../utils/request';

const router = useRouter();
const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png';
const userInfo = ref({
  username: '',
  role: '',
  avatar: ''
});

const fetchUserInfo = async () => {
  const token = localStorage.getItem('token');
  if (!token) return; // 🌟 如果没有 token，不发请求，避免登录前弹出报错
  
  try {
    const res = await request.get('/profile/');
    userInfo.value = res;
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
};

const handleCommand = (command) => {
  if (command === 'logout') {
    handleLogout();
  } else if (command === 'profile') {
    router.push('/profile');
  }
};

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录并切换账号吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    // 清除本地存储的 Token 和用户信息
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    ElMessage.success('已安全退出');
    // 跳转回登录页
    router.push('/login');
  }).catch(() => {});
};

onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.breadcrumbs {
  display: flex;
  align-items: center;
}

.breadcrumb-icon {
  font-size: 14px;
  color: var(--text-secondary);
}

.breadcrumb-separator {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 8px;
}

.breadcrumb-text {
  font-size: 14px;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  align-items: center;
}

.status-tag {
  margin-right: 24px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.action-icons {
  display: flex;
  align-items: center;
}

.action-icon {
  font-size: 18px;
  color: var(--text-secondary);
  margin-right: 20px;
  cursor: pointer;
  transition: color 0.2s;
}

.action-icon:hover {
  color: var(--primary-color);
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.user-dropdown:hover {
  background-color: #f3f4f6;
}

.user-avatar {
  margin-right: 8px;
}

.user-info {
  margin-right: 6px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--text-secondary);
}

.dropdown-icon {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>