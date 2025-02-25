<template>
    <el-space style="width: 90%" fill>
      <div>
        <el-row>
          <el-button @click="setLoading">Click me to reload</el-button>
        </el-row>
      </div>
      <Loginformationdisplay v-if="serverlogdisplay" :ServerID="serverlogdisplay" />

      <el-skeleton
        style="display: flex; gap: 8px"
        :loading="loading"
        animated
        :count="servers.length"
      >
        <template #template>
          <div style="flex: 1">
            <el-skeleton-item variant="image" style="height: 240px" />
            <div style="padding: 14px">
              <el-skeleton-item variant="h3" style="width: 50%" />
              <div
                style="
                  display: flex;
                  align-items: center;
                  justify-items: space-between;
                  margin-top: 16px;
                  height: 16px;
                "
              >
                <el-skeleton-item variant="text" style="margin-right: 16px" />
                <el-skeleton-item variant="text" style="width: 30%" />
              </div>
            </div>
          </div>
        </template>
        <!-- 使用v-if来控制服务器框架的显示 -->
        <template #default v-if="showServers">
          <el-card
            v-for="server in servers"
            :key="server.id"
            :body-style="{ padding: '0px', marginBottom: '1px' }"
          >
            <img
              src="https://fuss10.elemecdn.com/0/6f/e35ff375812e6b0020b6b4e8f9583jpeg.jpeg"
              class="image multi-content"
              style="max-width: 60%"
            />
            <div style="padding: 14px">
              <span>{{ server.name }}</span>
              <div class="bottom card-header">
                <div class="time">{{ server.operating_system }}</div>
                <!-- 点击按钮后隐藏所有框架 -->
                <el-button text class="button" @click="hideServers(server.id)">查看日志</el-button>
              </div>
            </div>
          </el-card>
        </template>
      </el-skeleton>
    </el-space>
  </template>
  
  <script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { defineProps } from 'vue';
  import Loginformationdisplay from './Loginformationdisplay.vue'
  
  interface Server {
    id: number,
    name: string,
    operating_system: string,
  }

  const props = defineProps<{
    servers: Server[]
  }>();
  
  const loading = ref(true);
  const showServers = ref(true); // 控制服务器框架显示的状态
  const serverlogdisplay = ref<number | null>(null);
  
  // 模拟加载效果
  const setLoading = () => {
    loading.value = true;
    setTimeout(() => {
      loading.value = false;
    }, 2000);
    showServers.value = false;
  };
  
  // 点击查看日志按钮后隐藏所有服务器框架
  const hideServers = (id: number) => {
    showServers.value = false;
    serverlogdisplay.value = id; // 显示日志窗口
  };
  
  onMounted(() => {
    loading.value = false;
  });
  </script>
  
  <style scoped>
  </style>
  