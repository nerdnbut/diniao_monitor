<template>
  <div class="bg-main">
    <!-- 下拉菜单 -->
    <el-dropdown @command="handleCommand">
      <span class="el-dropdown-link">
        {{ selectedServerName }}
        <el-icon class="el-icon--right">
          <arrow-down />
        </el-icon>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <template v-for="server in servers" :key="server.id">
            <el-dropdown-item :command="server.id">
              {{ server.name }}
            </el-dropdown-item>
          </template>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 终端容器 -->
    <div
      ref="terminal"
      v-loading="loading"
      class="terminal"
      element-loading-text="拼命连接中"
    ></div>
  </div>
</template>


<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { debounce } from 'lodash';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';
import { ElMessage } from 'element-plus';
import { ArrowDown } from '@element-plus/icons-vue';

interface Server {
  id: number;
  name: string;
}

// 状态变量
const props = defineProps<{
  servers: Server[];
}>(); // 服务器数据

const selectedServerName = ref<string>('选择服务器');
const loading = ref(true);
const terminal = ref<HTMLElement | null>(null);
const fitAddon = new FitAddon();
let terminalSocket = ref<WebSocket | null>(null);
let term = ref<Terminal | null>(null);

// 处理服务器选择
const handleCommand = async (serverId: number) => {
  const selectedServer = props.servers.find(server => server.id === serverId);
  if (selectedServer) {
    selectedServerName.value = selectedServer.name;
    loading.value = true;

    if (terminalSocket.value && terminalSocket.value.readyState === WebSocket.OPEN) {
      terminalSocket.value.close();
    }

    try {
      // 建立新的 WebSocket 连接
      terminalSocket.value = new WebSocket(`ws://localhost:8000/ws/ssh/`);

      terminalSocket.value.onopen = () => {
        term.value?.writeln('\x1b[32;1mWebSocket 连接已建立\x1b[0m');
        terminalSocket.value?.send(JSON.stringify({ server_id: serverId }));
      };

      terminalSocket.value.onmessage = (message) => {
        const data = JSON.parse(message.data);
        if (data.output) {
          term.value?.write(data.output);
        } else if (data.status) {
          term.value?.writeln(`\x1b[32;1m${data.status}\x1b[0m`);
        } else if (data.error) {
          term.value?.writeln(`\x1b[31;1m错误: ${data.error}\x1b[0m`);
        }
      };

      terminalSocket.value.onerror = (event) => {
        console.error('WebSocket 错误', event);
        term.value?.writeln(`\x1b[31;1mWebSocket 错误: ${event}\x1b[0m`);
      };

      terminalSocket.value.onclose = () => {
        term.value?.writeln('\x1b[31;1mWebSocket 连接已关闭\x1b[0m');
        loading.value = false;
      };

      loading.value = false;

      // 初始化终端
      if (!term.value) {
        initTerm();
      }

      let inputBuffer = '';  // 输入缓存区
      term.value?.onData((data) => {
        if (data === '\u0008' || data === '\x7F') {  // 处理 Backspace (ASCII '\u0008') 和 Delete (ASCII '\x7F')
          if (inputBuffer.length > 0) {
            inputBuffer = inputBuffer.slice(0, -1);  // 删除缓存区最后一个字符
            term.value?.write('\b \b');  // 在终端中删除最后一个字符
          }
        } else {
          term.value?.write(data);  // 回显输入内容到终端
          inputBuffer += data;  // 缓存输入的数据
        }

        if (data === '\r' || data === '\n') {  // 检测回车键
          terminalSocket.value?.send(JSON.stringify({ input: inputBuffer }));
          inputBuffer = '';  // 清空缓存
        }
      });

    } catch (error) {
      console.error('连接失败', error);
      ElMessage.error('连接失败，请重试');
      loading.value = false;
    }
  }
};

// 在初始化终端时调用 termData
const initTerm = () => {
  term.value = new Terminal({
    fontSize: 14,
    fontFamily: "Monaco, Menlo, Consolas, 'Courier New', monospace",
    theme: {
      background: '#181d28',
      foreground: '#ffffff',  // 文字颜色
      cursor: '#ffffff',  // 光标颜色  // 选择区域的背景色
    },
    cursorBlink: true,
    cursorStyle: 'underline',
  });
  term.value.open(terminal.value as HTMLElement);
  term.value.loadAddon(fitAddon);

  setTimeout(() => {
    fitAddon.fit();
  }, 5);

  termData(); // 调用 termData 初始化输入处理
};

// 终端输入触发事件
// let inputBuffer = '';

const termData = () => {

  term.value?.onResize(() => {
    resizeRemoteTerminal(); // 调整终端大小
  });
};

// 尺寸同步 发送给后端,调整后端终端大小,和前端保持一致
const resizeRemoteTerminal = () => {
  const { cols, rows } = term.value || {};
  if (isWsOpen()) {
    terminalSocket.value?.send(
      JSON.stringify({
        type: 'resize',
        data: {
          rows: rows,
          cols: cols,
        },
      })
    );
  }
};

// 检查 WebSocket 是否已打开
const isWsOpen = () => {
  const readyState = terminalSocket.value?.readyState;
  return readyState === 1;
};

// 适应浏览器尺寸变化
const fitTerm = () => {
  fitAddon.fit();
};

const onResize = debounce(() => fitTerm(), 500);

const onTerminalResize = () => {
  window.addEventListener('resize', onResize);
};

const removeResizeListener = () => {
  window.removeEventListener('resize', onResize);
};

onMounted(() => {
  initTerm();
  onTerminalResize();
});

onBeforeUnmount(() => {
  removeResizeListener();
  terminalSocket.value?.close();
});
</script>

<style lang="scss" scoped>
.terminal {
  width: 100%;
  height: calc(100% - 62px);
  text-align: left;  /* 确保内容左对齐 */
}

.el-dropdown-link {
  cursor: pointer;
  display: inline-block;
}

.el-dropdown-menu {
  z-index: 1;
}
</style>
