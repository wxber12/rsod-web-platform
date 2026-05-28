<template>
  <div class="sidebar-container">
    <div class="logo-section">
      <div class="logo-icon">
        <el-icon :size="28" color="white"><Sunny /></el-icon>
      </div>
      <div class="logo-text">
        <div class="logo-title">病虫害识别</div>
        <div class="logo-subtitle">智能诊断 精准防治</div>
      </div>
    </div>

    <div class="nav-menu">
      <div
        v-for="item in menuList"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentPath === item.path }"
        @click="handleMenuClick(item)"
      >
        <el-icon :size="22" class="nav-icon"><component :is="item.icon" /></el-icon>
        <span class="nav-text">{{ item.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  Sunny,
  Picture,
  Clock,
  ChatDotRound,
  DataLine,
  User,
} from "@element-plus/icons-vue";

const router = useRouter();
const route = useRoute();

const menuList = [
  {
    name: "智能检测",
    icon: Picture,
    path: "/detection",
  },
  {
    name: "历史记录",
    icon: Clock,
    path: "/history",
  },
  {
    name: "AI 问答",
    icon: ChatDotRound,
    path: "/qa",
  },
  {
    name: "目标库",
    icon: DataLine,
    path: "/targets",
  },
  {
    name: "个人中心",
    icon: User,
    path: "/profile",
  },
];

const currentPath = computed(() => route.path);

const handleMenuClick = (item) => {
  router.push(item.path);
};
</script>

<style scoped>
/* 农业主题样式（与 LoginPage1.0 保持一致） */
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(255, 252, 245, 0.88);
  backdrop-filter: blur(16px);
  border-right: 1px solid rgba(255, 245, 215, 0.6);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
}

.logo-section {
  padding: 28px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #1a3a32, #2b5a48);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.logo-text {
  overflow: hidden;
}

.logo-title {
  font-size: 18px;
  font-weight: 800;
  color: #1a3a32;
  line-height: 1.3;
  white-space: nowrap;
  letter-spacing: -0.3px;
}

.logo-subtitle {
  font-size: 12px;
  color: #5d6e4a;
  margin-top: 4px;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.nav-menu {
  flex: 1;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-radius: 28px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #3b5a4a;
  gap: 14px;
}

.nav-item:hover {
  background: rgba(46, 125, 50, 0.12);
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(26, 58, 50, 0.9), rgba(43, 90, 72, 0.9));
  color: white;
  box-shadow: 0 6px 14px rgba(26, 58, 50, 0.2);
}

.nav-item.active .nav-icon {
  color: #cfb53b;
}

.nav-icon {
  font-size: 24px;
  color: #5d6e4a;
  flex-shrink: 0;
}

.nav-text {
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 0.3px;
}

@media (max-width: 768px) {
  .logo-section {
    padding: 20px 16px;
  }
  .logo-icon {
    width: 44px;
    height: 44px;
  }
  .logo-title {
    font-size: 15px;
  }
  .logo-subtitle {
    font-size: 10px;
  }
  .nav-item {
    padding: 12px 16px;
  }
  .nav-text {
    font-size: 16px;
  }
}
</style>