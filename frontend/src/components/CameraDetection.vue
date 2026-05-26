<template>
  <div class="camera-detection">
    <div class="detection-container">
      <div class="video-wrapper">
        <video
          ref="videoRef"
          autoplay
          playsinline
          class="source-video"
        ></video>
        <canvas
          ref="canvasRef"
          class="detection-canvas"
        ></canvas>
        
        <div v-if="!isRunning" class="camera-placeholder">
          <el-icon :size="64"><VideoCamera /></el-icon>
          <p>摄像头未启动</p>
          <el-button type="primary" @click="toggleCamera">
            启动实时检测
          </el-button>
        </div>
        
        <div v-if="isDetecting && isRunning" class="detection-overlay">
          <div class="scanning-line"></div>
        </div>
      </div>

      <div class="control-panel">
        <div class="status-info">
          <div class="info-item">
            <span class="label">状态:</span>
            <el-tag :type="isRunning ? 'success' : 'info'">
              {{ isRunning ? '运行中' : '已停止' }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="label">FPS:</span>
            <span class="value">{{ fps }}</span>
          </div>
          <div class="info-item">
            <span class="label">目标数:</span>
            <span class="value">{{ totalObjects }}</span>
          </div>
          <div class="info-item">
            <span class="label">耗时:</span>
            <span class="value">{{ detectionTime }}s</span>
          </div>
        </div>

        <div class="action-buttons">
          <el-button 
            :type="isRunning ? 'danger' : 'primary'" 
            @click="toggleCamera"
          >
            <el-icon>
              <component :is="isRunning ? 'CircleClose' : 'VideoCamera'" />
            </el-icon>
            {{ isRunning ? '停止检测' : '启动检测' }}
          </el-button>
          
          <el-button 
            v-if="isRunning"
            :type="isPaused ? 'success' : 'warning'" 
            @click="isPaused = !isPaused"
          >
            <el-icon>
              <component :is="isPaused ? 'VideoPlay' : 'VideoPause'" />
            </el-icon>
            {{ isPaused ? '恢复' : '暂停' }}
          </el-button>
        </div>
        
        <div class="config-panel" v-if="isRunning">
          <div class="config-item">
            <span class="config-label">推理间隔 (帧)</span>
            <el-slider v-model="inferenceInterval" :min="1" :max="10" />
          </div>
        </div>
      </div>
    </div>

    <!-- 用于截帧的隐藏 Canvas -->
    <canvas ref="captureCanvasRef" style="display: none;"></canvas>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount, nextTick } from 'vue';
import { 
  VideoCamera, 
  CircleClose, 
  VideoPause, 
  VideoPlay 
} from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { detectFrame } from '../api/detection';

const videoRef = ref(null);
const canvasRef = ref(null);
const captureCanvasRef = ref(null);

const isRunning = ref(false);
const isPaused = ref(false);
const isDetecting = ref(false);
const fps = ref(0);
const totalObjects = ref(0);
const detectionTime = ref(0);
const inferenceInterval = ref(2);

let videoStream = null;
let animationId = null;
let frameCount = 0;
let lastDetectionTime = 0;

const startCamera = async () => {
  try {
    videoStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 30 }
      },
      audio: false
    });

    if (videoRef.value) {
      videoRef.value.srcObject = videoStream;
      videoRef.value.onloadedmetadata = () => {
        isRunning.value = true;
        initCanvas();
        startDetectionLoop();
      };
    }
  } catch (error) {
    console.error('摄像头启动失败:', error);
    ElMessage.error('无法访问摄像头，请检查权限设置');
  }
};

const stopCamera = () => {
  if (videoStream) {
    videoStream.getTracks().forEach(track => track.stop());
    videoStream = null;
  }
  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }
  isRunning.value = false;
  isPaused.value = false;
  const ctx = canvasRef.value?.getContext('2d');
  if (ctx) ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
};

const toggleCamera = () => {
  if (isRunning.value) {
    stopCamera();
  } else {
    startCamera();
  }
};

const initCanvas = () => {
  if (videoRef.value && canvasRef.value) {
    canvasRef.value.width = videoRef.value.videoWidth;
    canvasRef.value.height = videoRef.value.videoHeight;
    captureCanvasRef.value.width = 320; // 降低推理分辨率
    captureCanvasRef.value.height = 240;
  }
};

const startDetectionLoop = () => {
  const loop = async () => {
    if (!isRunning.value) return;

    if (!isPaused.value) {
      frameCount++;
      
      // 每隔 inferenceInterval 帧执行一次检测
      if (frameCount % inferenceInterval.value === 0) {
        await performDetection();
      }
    } else {
      // 暂停时清空检测框
      const ctx = canvasRef.value?.getContext('2d');
      if (ctx) ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
    }

    animationId = requestAnimationFrame(loop);
  };
  animationId = requestAnimationFrame(loop);
};

const performDetection = async () => {
  if (!videoRef.value || !captureCanvasRef.value) return;

  const captureCanvas = captureCanvasRef.value;
  const ctx = captureCanvas.getContext('2d');
  
  // 截取当前帧
  ctx.drawImage(videoRef.value, 0, 0, captureCanvas.width, captureCanvas.height);
  
  // 转换为 Base64
  const imageData = captureCanvas.toDataURL('image/jpeg', 0.7);
  
  try {
    isDetecting.value = true;
    const response = await detectFrame({ image: imageData });
    
    if (response.success) {
      const data = response.data;
      fps.value = data.fps;
      totalObjects.value = data.total_objects;
      detectionTime.value = data.detection_time;
      drawBoxes(data.boxes);
    }
  } catch (error) {
    console.error('检测请求失败:', error);
  } finally {
    isDetecting.value = false;
  }
};

const drawBoxes = (boxes) => {
  if (!canvasRef.value || !videoRef.value) return;

  const canvas = canvasRef.value;
  const ctx = canvas.getContext('2d');
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  const scaleX = canvas.width / videoRef.value.videoWidth;
  const scaleY = canvas.height / videoRef.value.videoHeight;

  boxes.forEach(box => {
    const x1 = box.x1 * scaleX;
    const y1 = box.y1 * scaleY;
    const x2 = box.x2 * scaleX;
    const y2 = box.y2 * scaleY;
    const width = x2 - x1;
    const height = y2 - y1;

    // 绘制框
    ctx.strokeStyle = '#4f46e5';
    ctx.lineWidth = 2;
    ctx.strokeRect(x1, y1, width, height);

    // 绘制标签
    const label = `${box.chinese_name} ${(box.confidence * 100).toFixed(0)}%`;
    ctx.font = '14px Arial';
    const labelWidth = ctx.measureText(label).width + 10;
    
    ctx.fillStyle = '#4f46e5';
    ctx.fillRect(x1, y1 - 25, labelWidth, 25);
    
    ctx.fillStyle = '#ffffff';
    ctx.fillText(label, x1 + 5, y1 - 7);
  });
};

onBeforeUnmount(() => {
  stopCamera();
});
</script>

<style scoped lang="scss">
.camera-detection {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}

.detection-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.video-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  background: #000;
  border-radius: 8px;
  overflow: hidden;

  .source-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .detection-canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }

  .camera-placeholder {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #6b7280;
    background: #f3f4f6;
    gap: 16px;
  }

  .detection-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    
    .scanning-line {
      width: 100%;
      height: 2px;
      background: linear-gradient(to right, transparent, #4f46e5, transparent);
      position: absolute;
      animation: scan 3s linear infinite;
      box-shadow: 0 0 15px #4f46e5;
    }
  }
}

.control-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9fafb;
  border-radius: 8px;

  .status-info {
    display: flex;
    gap: 20px;
    
    .info-item {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .label {
        font-size: 14px;
        color: #6b7280;
      }
      
      .value {
        font-weight: 600;
        color: #111827;
      }
    }
  }

  .action-buttons {
    display: flex;
    gap: 12px;
  }

  .config-panel {
    width: 200px;
    
    .config-item {
      display: flex;
      flex-direction: column;
      gap: 5px;
      
      .config-label {
        font-size: 12px;
        color: #9ca3af;
      }
    }
  }
}

@keyframes scan {
  from { top: 0; }
  to { top: 100%; }
}
</style>
