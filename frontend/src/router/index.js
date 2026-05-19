// router/index.js
import { createRouter, createWebHistory } from "vue-router";
import index from "../views/index.vue"; // 你的检测页面
import Detection from "../views/Detection.vue";
import inference from "../views/Inference.vue"; // Yolo 推理验证⻚⾯
// 路由配置

const routes = [
  {
    path: "/",
    name: "index",
    component: index, // 默认打开就是检测页面
  },
  {
    path: "/detection",
    name: "detection",
    component: Detection, // 默认打开这个带切换模式的页面
  },
  {
    path: "/inference",
    name: "inference",
    component: inference, // 默认打开就是检测⻚⾯
  },
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;