<template>
    <div>
      <h1>服务器日志</h1>
      
      <el-table
        :data="tableData"
        style="width: 100%;overflow: auto;"
        :default-sort="{ prop: 'timestamp', order: 'descending' }"
        v-loading="loading"
      >
        <el-table-column prop="timestamp" label="时间戳" sortable width="220" />
        <el-table-column prop="log_level" label="日志级别" width="120" />
        <el-table-column prop="message" label="消息" />
        <el-table-column fixed="right" prop="function" label="操作">
          <template #default>
            <el-button type="danger" link size="small" @click="handleDelete">删除</el-button>
            <el-button type="primary" link size="small" @click="handleDownload">下载</el-button>
          </template>
        </el-table-column>
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
  
  // 删除功能
  const handleDelete = async (logId: number) => {
    try {
      await axios.delete(`/log/${props.ServerID}/${logId}/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      // 删除成功后重新获取数据
      fetchServerLogData(currentPage.value);
    } catch (e) {
      console.error(e);
      // 可以在这里添加错误提示
    }
  }
  
  // 下载
  const handleDownload = async (logId: number) => {
    try {
      const response = await axios.get(`/log/${props.ServerID}/${logId}/download/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        },
        responseType: 'blob'  // 确保响应类型为blob
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `log_${logId}.txt`);  // 设置下载文件名
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) {
      console.error(e);
      // 可以在这里添加错误提示
    }
  }
  // 在组件挂载时获取初始数据
  onMounted(() => {
    fetchServerLogData(currentPage.value);
  });
  </script>
  
  <style scoped>
  /* 可以根据需要添加样式 */
  </style>
  