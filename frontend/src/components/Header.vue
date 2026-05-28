<template>
  <div class="header-container">
    <div class="breadcrumbs">
      <el-icon class="breadcrumb-icon"><House /></el-icon>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-text">{{ route.name || '智能检测' }}</span>
    </div>

    <div class="header-actions">
      <el-tag type="success" effect="light" class="status-tag">
        <el-icon class="el-icon--left"><Check /></el-icon>
        系统运行中
      </el-tag>

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
import { useRouter, useRoute } from 'vue-router';
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
const route = useRoute();
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
/* 农业主题样式（与 LoginPage1.0 保持一致） */
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 12px 28px;
  background: rgba(255, 252, 245, 0.96);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(255, 245, 215, 0.8);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breadcrumb-icon {
  font-size: 18px;
  color: #5d6e4a;
}

.breadcrumb-separator {
  font-size: 16px;
  color: #9ca3af;
}

.breadcrumb-text {
  font-size: 18px;
  font-weight: 600;
  color: #1a3a32;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 24px;
}

.status-tag {
  padding: 8px 18px;
  border-radius: 40px;
  font-size: 14px;
  font-weight: 500;
  background: #e8f5e9;
  color: #2e7d32;
  border: none;
}

.action-icons {
  display: flex;
  align-items: center;
  gap: 20px;
}

.action-icon {
  font-size: 22px;
  color: #5d6e4a;
  cursor: pointer;
  transition: all 0.2s;
}

.action-icon:hover {
  color: #cfb53b;
  transform: translateY(-2px);
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 6px 16px;
  border-radius: 60px;
  background: rgba(255, 255, 255, 0.6);
  transition: all 0.2s;
}

.user-dropdown:hover {
  background: rgba(46, 125, 50, 0.1);
}

.user-avatar {
  border: 2px solid #cfb53b;
}

.user-name {
  font-size: 16px;
  font-weight: 700;
  color: #1a3a32;
}

.user-role {
  font-size: 13px;
  color: #5d6e4a;
}

.dropdown-icon {
  font-size: 14px;
  color: #5d6e4a;
  transition: transform 0.2s;
}

.user-dropdown:hover .dropdown-icon {
  transform: rotate(180deg);
  color: #cfb53b;
}

@media (max-width: 768px) {
  .header-container {
    padding: 10px 16px;
  }
  .breadcrumb-text {
    font-size: 16px;
  }
  .status-tag {
    padding: 6px 12px;
    font-size: 12px;
  }
  .action-icon {
    font-size: 18px;
  }
  .user-name {
    font-size: 14px;
  }
}
</style>