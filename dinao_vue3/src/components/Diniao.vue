<template>
    <div class="common-layout">
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header class="header">
            <el-page-header title="Diniao" icon="none">
                <template #content>
                <el-avatar :size="50" class="mr-3" src="../../public/images/logo.png" @click="userinfoClick" />
                    <span class="text-large font-600 mr-3">{{ top_name }}</span>
                </template>
            </el-page-header>
        </el-header>
        <el-container>
            <!-- 侧边栏 -->
        <div class="content">
          <el-aside width="100%" class="sidbar">
            <el-row>
                <el-col :span="30">
                  <el-menu 
                    active-text-color="#ffd04b"
                    background-color="#01344f"
                    text-color="#fff"
                    :default-active="selectedIndex" 
                    class="el-menu-vertical-demo" 
                    @open="handleOpen" 
                    @close="handleClose">
                    <el-sub-menu index="1" :popper-append-to-body="false">
                      <template #title>
                        <el-icon><PieChart /></el-icon>
                        <span>服务器</span>
                      </template>
                      <el-menu-item
                        v-for="(server, index) in servers"
                        :key="server.id"
                        @click="handleMenuItemClick(server.id)"
                        :index="`1-${index + 1}`"
                      >
                        {{ server.name }}
                      </el-menu-item>
                    </el-sub-menu>
                    <el-sub-menu index="2" :popper-append-to-body="false">
                      <template #title>
                        <el-icon><Desktop /></el-icon>
                        <span>报警管理</span>
                      </template>
                      <el-menu-item index="2-1">
                        <el-icon><icon-menu /></el-icon>
                        <span @click="alarmtaskClick">报警设置</span>
                      </el-menu-item>
                      <el-menu-item index="2-2">
                        <el-icon><icon-menu /></el-icon>
                        <span @click="alarmsetClick">报警记录</span>
                      </el-menu-item>
                    </el-sub-menu>
                    <el-menu-item index="2">
                      <el-icon><icon-menu /></el-icon>
                      <span @click="serverterminalClick">终端</span>
                    </el-menu-item>
                    <el-menu-item index="4">
                      <el-icon><Document /></el-icon>
                      <span @click="serverlogclick">日志</span>
                    </el-menu-item>
                    <el-menu-item index="5">
                      <!-- <el-icon><setting /></el-icon> -->
                      <!-- <span>设置</span> -->
                    </el-menu-item>
                  </el-menu>
                </el-col>
                </el-row>
          </el-aside>
        </div>
          <!-- 主体内容 -->
          <el-main class="main">
            <div>
              <!-- 用户信息组件 -->
              <Userinfo v-if="userinfo" :servers="servers" />
              <!-- 动态渲染服务器监控组件 -->
              <ServerMonitoring v-if="selectedServerId" :serverId="selectedServerId" />
              <!-- 终端组件 -->
              <ServerTerminal v-if="serverterminal" :servers="servers" />
              <!-- 日志组件 -->
              <Logdatacollection v-if="serverlogdata" :servers="servers" />
              <!-- 报警设置组件 -->
              <Alarm_set_from v-if="alarmsetfrom" :servers="servers" />
              <!-- 报警任务组件 -->
               <AlarmTask v-if="alarmtask" :servers="servers" />
            </div>
          </el-main>
        </el-container>
      </el-container>
    </div>
  </template>
  
  <!-- 方法 -->
    <script lang="ts" setup>
    import {
      Document,
        Menu as IconMenu,
        PieChart,
        Setting,
    } from '@element-plus/icons-vue';
    import { ref, onMounted } from 'vue';
    import ServerMonitoring from './ServerMonitoring.vue'
    import ServerTerminal from './ServerTerminal.vue';
    import Logdatacollection from './Logdatacollection.vue';
    import Alarm_set_from from './Alarm_set_from.vue';
    import AlarmTask from './AlarmTask.vue';
    import Userinfo from './userinfo.vue';
    import axios from 'axios';
    axios.defaults.withCredentials = true

    // 顶部导航栏
    const top_name = ref<string | null>(null);
    onMounted(() => {
      // 从localStorage中获取用户名
      top_name.value = localStorage.getItem('username');
    })
    
    // 侧边栏方法
    const handleOpen = (key: string, keyPath: string[]) => {
        console.log(key, keyPath)
    }
    const handleClose = (key: string, keyPath: string[]) => {
        console.log(key, keyPath)
    }
    // 获取当前用户的所有服务器信息
    import { useServerStore } from '../stores/serverdata';
    import { computed } from 'vue'
    const serverStore = useServerStore()
    // 获取服务器数据
    onMounted( async () => {
      await serverStore.fetchServers();
            // 控制台输出servers中的第一条数据
      // console.log(servers.value[0])?.id;
      await handleMenuItemClick(servers.value[0]?.id);
    });
    const servers = computed(() => serverStore.servers);
    const userinfo = ref<boolean>(false);
    const selectedIndex = ref<string>("1-1");
    const selectedServerId = ref<number | null>(null);
    const serverterminal = ref<boolean>(false);
    const serverlogdata = ref<boolean>(false);
    const alarmsetfrom = ref<boolean>(false);
    const alarmtask = ref<boolean>(false);
    const userinfoClick = () =>{
      serverterminal.value = false;
      selectedServerId.value = null;
      serverlogdata.value = false;
      alarmsetfrom.value = false;
      alarmtask.value = false;
      userinfo.value = true;
    }
    const handleMenuItemClick = (id: number) => {
      selectedIndex.value = '1-${id}';
      selectedServerId.value = id;
      serverterminal.value = false;
      serverlogdata.value = false;
      alarmsetfrom.value = false;
      alarmtask.value = false;
      userinfo.value = false;
    };
    const serverterminalClick = () =>{
      serverterminal.value = true;
      selectedServerId.value = null;
      serverlogdata.value = false;
      alarmsetfrom.value = false;
      alarmtask.value = false;
      userinfo.value = false;
    }
    const serverlogclick = () => {
      serverlogdata.value = true;
      selectedServerId.value = null;
      serverterminal.value = false;
      alarmsetfrom.value = false;
      alarmtask.value = false;
      userinfo.value = false;
    }
    const alarmtaskClick = () => {
      selectedIndex.value = "2-1";
      alarmtask.value = true;
      selectedServerId.value = null;
      serverterminal.value = false;
      serverlogdata.value = false;
      alarmsetfrom.value = false;
      userinfo.value = false;
    }
    const alarmsetClick = () => {
      selectedIndex.value = "2-2";
      alarmsetfrom.value = true;
      selectedServerId.value = null;
      serverterminal.value = false;
      serverlogdata.value = false;
      alarmtask.value = false;
      userinfo.value = false;
    }
    // 主体内容

    </script>

  <!-- 样式 -->
   <style>
    /* 主体布局 */
    .header {
        background-color: #d12128;
    }

    .content {
        height: 100vh;
        background-color: #01344f;
    }
   </style>