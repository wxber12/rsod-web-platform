<template>
  <router-view v-if="isAuthPage" />
  <MainLayout v-else>
    <template #sidebar>
      <Sidebar />
    </template>
    <template #header>
      <Header />
    </template>
    <template #content>
      <router-view />
    </template>
  </MainLayout>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import MainLayout from "./layouts/MainLayout.vue";
import Sidebar from "./components/Sidebar.vue";
import Header from "./components/Header.vue";

const route = useRoute();

const isAuthPage = computed(() => {
  const authPaths = ["/login", "/register", "/forgot-password"];
  return authPaths.includes(route.path);
});
</script>

<style>
/* 全局样式：确保根元素占满全屏，移除默认边距 */
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

/* 可选：统一盒模型 */
* {
  box-sizing: border-box;
}
</style>