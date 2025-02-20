<template>
    <div>
      <h1>服务器日志</h1>
      
      <el-table
        :data="tableData"
        style="width: 100%"
        :default-sort="{ prop: 'timestamp', order: 'descending' }"
        v-loading="loading"
      >
        <el-table-column prop="timestamp" label="时间戳" sortable width="220" />
        <el-table-column prop="log_level" label="日志级别" width="120" />
        <el-table-column prop="message" label="消息" />
      </el-table>
      
      <!-- 分页控件 -->
      <div style="margin-top: 20px; text-align: center;">
        <el-pagination
          background
          layout="prev, pager, next"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @current-change="handlePageChange"
        >
        </el-pagination>
      </div>
    </div>
  </template>
  
  <script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { defineProps } from 'vue';
  import axios from 'axios';
  
  // 定义服务器ID属性
  const props = defineProps<{ ServerID: number }>();
  
  // 定义响应式变量
  const tableData = ref<any[]>([]);
  const currentPage = ref(1);
  const pageSize = ref(20);  // 默认每页显示条数
  const total = ref(0);
  const loading = ref(false);
  
  // 获取日志数据的函数
  const fetchServerLogData = async (page: number) => {
    if (page < 1) return;  // 防止页码为负数
  
    loading.value = true;
  
    try {
      const response = await axios.get(`/log/${props.ServerID}/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        },
        params: {
          page: page,
          page_size: pageSize.value  // 传递每页条数参数
        }
      });
  
      // 处理响应数据
      tableData.value = response.data.results.map((log: any) => ({
        id: log.id,
        timestamp: new Date(log.timestamp).toLocaleString(),
        log_level: log.log_level,
        message: log.message
      }));
      currentPage.value = page;
      total.value = response.data.count;
    } catch (e) {
      console.error(e);
      // 可以在这里添加错误提示
    } finally {
      loading.value = false;
    }
  };
  
  // 处理页码变化
  const handlePageChange = (page: number) => {
    fetchServerLogData(page);
  };
  
  // 在组件挂载时获取初始数据
  onMounted(() => {
    fetchServerLogData(currentPage.value);
  });
  </script>
  
  <style scoped>
  /* 可以根据需要添加样式 */
  </style>
  