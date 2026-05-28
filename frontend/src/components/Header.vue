<template>
  <div class="header-container">
    <div class="breadcrumbs">
      <el-icon class="breadcrumb-icon"><House /></el-icon>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-text">智能检测</span>
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
        <div class="user-dropdown">
          <el-avatar class="user-avatar" :size="40">
            <img
              src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
              alt="用户头像"
            />
          </el-avatar>
          <div class="user-info">
            <div class="user-name">研究员</div>
            <div class="user-role">植保专家</div>
          </div>
          <el-icon class="dropdown-icon"><CaretBottom /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Check,
  Grid,
  Bell,
  QuestionFilled,
  CaretBottom,
  House,
} from "@element-plus/icons-vue";
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