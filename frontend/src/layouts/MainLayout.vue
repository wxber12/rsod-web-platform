<template>
  <div class="main-layout">
    <aside class="sidebar">
      <slot name="sidebar"></slot>
    </aside>

    <div class="main-container">
      <header class="header">
        <slot name="header"></slot>
      </header>

      <main class="content">
        <slot name="content"></slot>
      </main>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.main-layout {
  --border-color: rgba(255, 245, 215, 0.6);
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 200px;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 64px;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.content {
  flex: 1;
  padding: 0;
  overflow-y: overlay;
  background-color: transparent;
}
</style>