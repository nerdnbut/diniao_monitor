<template>
  <el-container class="app-container">
    <!-- 顶部导航栏简化 -->
    <el-header class="header">
      <div class="header-content">
        <h1 class="logo">Diniao</h1>
        <el-avatar :size="40" src="../../public/images/logo.png" @click="userinfoClick" />
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 侧边栏优化 -->
      <el-aside width="220px" class="sidebar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          @select="handleMenuSelect"
          :collapse="isCollapse">
          <el-sub-menu index="servers">
            <template #title>
              <el-icon><Monitor /></el-icon>
              <span>服务器</span>
            </template>
            <el-menu-item
              v-for="server in servers"
              :key="server.id"
              :index="`server-${server.id}`"
            >
              {{ server.name }}
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="alarms">
            <template #title>
              <el-icon><Bell /></el-icon>
              <span>报警管理</span>
            </template>
            <el-menu-item index="alarm-settings">报警设置</el-menu-item>
            <el-menu-item index="alarm-records">报警记录</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="terminal">
            <el-icon><Notebook /></el-icon>
            <template #title>终端</template>
          </el-menu-item>

          <el-menu-item index="logs">
            <el-icon><Document /></el-icon>
            <template #title>日志</template>
          </el-menu-item>

          <el-menu-item index="files">
            <el-icon><Files /></el-icon>
            <template #title>文件管理</template>
          </el-menu-item>

          <el-menu-item index="scripts">
            <el-icon><DocumentAdd /></el-icon>
            <template #title>任务管理</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区优化 -->
      <el-main class="main-content">
        <component 
          :is="currentComponent" 
          :servers="servers"
          :serverId="selectedServerId"
        />
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts" setup>
import {
  Document,
  Monitor,
  Bell,
  Notebook,
  Files,
  DocumentAdd
} from '@element-plus/icons-vue';
import { ref, onMounted } from 'vue';
import ServerMonitoring from './ServerMonitoring.vue'
import ServerTerminal from './ServerTerminal.vue';
import Logdatacollection from './Logdatacollection.vue';
import Alarm_set_from from './Alarm_set_from.vue';
import AlarmTask from './AlarmTask.vue';
import Userinfo from './userinfo.vue';
import fileSystem from './file-system.vue';
import taskManagement from './task-management.vue';
import axios from 'axios';
axios.defaults.withCredentials = true

// 顶部导航栏
const top_name = ref<string | null>(null);
onMounted(() => {
  // 从localStorage中获取用户名
  top_name.value = localStorage.getItem('username');
})

// 状态管理
const activeMenu = ref('dashboard')
const isCollapse = ref(false)
const currentComponent = ref<any>('ServerMonitoring')
const selectedServerId = ref<number | null>(null)

// 获取当前用户的所有服务器信息
import { useServerStore } from '../stores/serverdata';
import { computed } from 'vue'
const serverStore = useServerStore()
// 获取服务器数据
onMounted( async () => {
  await serverStore.fetchServers();
        // 控制台输出servers中的第一条数据
  // console.log(servers.value[0])?.id;
  await handleMenuSelect(`server-${servers.value[0]?.id}`);
});
const servers = computed(() => serverStore.servers);
const userinfo = ref<boolean>(false);

// 菜单处理函数
const handleMenuSelect = (index: string) => {
  if (index.startsWith('server-')) {
    const serverId = parseInt(index.split('-')[1])
    selectedServerId.value = serverId
    currentComponent.value = ServerMonitoring
  } else {
    const componentMap: Record<string, any> = {
      'terminal': ServerTerminal,
      'logs': Logdatacollection,
      'alarm-settings': AlarmTask,
      'alarm-records': Alarm_set_from,
      'dashboard': Userinfo,
      'files': fileSystem,
      'scripts': taskManagement
    }
    currentComponent.value = componentMap[index] || ServerMonitoring
    selectedServerId.value = null
  }
}

const userinfoClick = () => {
  currentComponent.value = Userinfo
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  color: #409eff;
  margin: 0;
  font-size: 24px;
}

.main-container {
  height: calc(100vh - 60px);
}

.sidebar {
  background-color: #ffffff;
  transition: all 0.3s;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  border-right: none;
}

.sidebar-menu {
  border-right: none;
}

.main-content {
  background-color: #ffffff;
  border-radius: 8px;
  margin: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 菜单样式重写 */
:deep(.el-menu) {
  background-color: transparent;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: #606266;
  height: 50px;
  line-height: 50px;
}

:deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  color: #409eff;
  border-right: 3px solid #409eff;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: #f5f7fa;
  color: #409eff;
}

:deep(.el-menu-item .el-icon),
:deep(.el-sub-menu__title .el-icon) {
  color: #909399;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: #409eff;
}

/* 图标样式 */
:deep(.el-icon) {
  font-size: 18px;
  margin-right: 4px;
}

/* 添加平滑过渡效果 */
:deep(.el-menu-item),
:deep(.el-sub-menu__title),
:deep(.el-icon) {
  transition: all 0.3s ease;
}
</style>