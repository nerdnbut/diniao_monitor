<template>
  <div>
    <h3>服务器终端</h3>
    <!-- 下拉菜单 -->
    <el-dropdown @command="handleCommand">
      <span class="el-dropdown-link">
        {{ selectedServerName }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <!-- 渲染服务器列表 -->
          <template v-for="server in servers" :key="server.id">
            <el-dropdown-item :command="server.id">{{ server.name }}</el-dropdown-item>
          </template>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 终端容器 -->
    <div ref="terminalContainer" class="terminal-container">
      <!-- 初始状态内容 -->
      <div v-if="!isConnected" class="placeholder">
        <img src="../../public/images/egg-icon.png" class="egg-icon" alt="Egg Icon" />
        <div class="colorful-text">
          <span class="text-red">请</span>
          <span class="text-green">选</span>
          <span class="text-blue">择</span>
          <span class="text-yellow">服</span>
          <span class="text-purple">务</span>
          <span class="text-cyan">器</span>
        </div>
        <div class="arrow-indicator"></div>
      </div>

      <!-- 连接中内容 -->
      <div v-if="isConnecting && !isConnected" class="connecting-placeholder">
        <div class="jumping-eggs">
          <img v-for="n in 6" :key="n" src="../../public/images/egg-icon.png" class="jumping-egg" alt="Jumping Egg" />
        </div>
        <div class="waiting-text">等待中...</div>
      </div>

      <!-- 终端内容 -->
      <div v-if="isConnected" class="xterm-wrapper"></div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { ElMessage } from 'element-plus';
import { ArrowDown } from '@element-plus/icons-vue';

interface Server {
  id: number;
  name: string;
}

const props = defineProps<{
  servers: Server[];
}>();

// 状态变量
const selectedServerName = ref<string>('选择服务器');
const terminalContainer = ref<HTMLElement | null>(null);
let terminal: Terminal | null = null;
let fitAddon: FitAddon | null = null;
const isConnecting = ref(false);
const isConnected = ref(false);
let ws: WebSocket | null = null;  // WebSocket 实例

// 处理服务器选择
const handleCommand = async (serverId: number) => {
  const selectedServer = props.servers.find(server => server.id === serverId);
  if (selectedServer) {
    selectedServerName.value = selectedServer.name;
    isConnecting.value = true;

    // 如果 WebSocket 已经打开，关闭它
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }

    try {
      // 建立新的 WebSocket 连接
      ws = new WebSocket(`ws://localhost:8000/ws/ssh/`);

      ws.onopen = () => {
        terminal?.writeln('\x1b[32;1mWebSocket 连接已建立\x1b[0m');
        ws?.send(JSON.stringify({ server_id: serverId }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("接收到的数据：", data);
        if (data.output) {
          terminal?.write(data.output);
        } else if (data.status) {
          terminal?.writeln(`\x1b[32;1m${data.status}\x1b[0m`);
        } else if (data.error) {
          terminal?.writeln(`\x1b[31;1m错误: ${data.error}\x1b[0m`);
        }
      };

      ws.onerror = (event) => {
        console.error("WebSocket 错误", event);
        terminal?.writeln(`\x1b[31;1mWebSocket 错误: ${event}\x1b[0m`);
      };

      ws.onclose = (event) => {
        terminal?.writeln('\x1b[31;1mWebSocket 连接已关闭\x1b[0m');
        isConnected.value = false;
        isConnecting.value = false;
      };

      isConnected.value = true;
      isConnecting.value = false;

      // 初始化终端
      if (!terminal) {
        terminal = new Terminal({
          theme: {
            background: '#f0f0f0',  // 浅灰色背景
            foreground: '#ffffff',  // 白色字体'
            cursor: '#ff0000',      // 光标颜色,黄色
            selection: '#d3d7cf'    // 选中的文本背景色，稍深的灰色
          }
        });
        fitAddon = new FitAddon();
        terminal.loadAddon(fitAddon);
        terminal.open(terminalContainer.value as HTMLElement);
        fitAddon.fit();
      }

      terminal.onData((data) => {
        if (ws?.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ input: data }));
        }
      });
      
    } catch (error) {
      console.error('连接失败', error);
      ElMessage.error('连接失败，请重试');
      isConnecting.value = false;
    }
  }
};

// 窗口调整大小处理
function handleResize() {
  fitAddon?.fit();
}

// 挂载生命周期钩子
onMounted(() => {
  window.addEventListener('resize', handleResize);

  if (!terminal) {
    terminal = new Terminal();
    fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);
    terminal.open(terminalContainer.value as HTMLElement);
    fitAddon.fit();
    terminal.writeln('\x1b[32;1m终端已初始化\x1b[0m');
  }
});

// 组件卸载时清理
onBeforeUnmount(() => {
  terminal?.dispose();
  window.removeEventListener('resize', handleResize);
  ws?.close();
});
</script>


<style scoped>
.terminal-container {
  height: 400px; 
  width: 100%;
  background-color: black;
  position: relative;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.egg-icon {
  width: 50px;
  height: 50px;
  margin-bottom: 20px;
}

.colorful-text {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.text-red { color: red; }
.text-green { color: green; }
.text-blue { color: blue; }
.text-yellow { color: yellow; }
.text-purple { color: purple; }
.text-cyan { color: cyan; }

.arrow-indicator {
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 15px solid red;
  margin-top: 10px;
}

.connecting-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.jumping-eggs {
  display: flex;
  justify-content: space-around;
  width: 100%;
}

.jumping-egg {
  width: 40px;
  height: 40px;
  animation: jump 1s infinite;
}

@keyframes jump {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.waiting-text {
  font-size: 18px;
  color: white;
  margin-top: 20px;
}

.xterm-wrapper {
  height: 100%;
}

.el-dropdown-menu {
  z-index: 1; 
}
</style>
