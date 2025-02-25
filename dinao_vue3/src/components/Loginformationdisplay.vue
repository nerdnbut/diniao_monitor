<template>
  <el-container>
    <el-header>
      <h1>服务器日志</h1>
    </el-header>
    <el-main>
      <el-table :data="tableData" style="width: 100%;" :default-sort="{ prop: 'timestamp', order: 'descending' }" v-loading="loading">
        <el-table-column prop="timestamp" label="时间戳" sortable width="220" />
        <el-table-column prop="log_level" label="日志级别" width="120" />
        <el-table-column prop="message" label="消息" />
        <el-table-column fixed="right" label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
            <el-button link type="primary" size="small" @click="handleDownload(row.id)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination background layout="prev, pager, next" :current-page="currentPage" :page-size="pageSize" :total="total" @current-change="handlePageChange" style="margin-top: 20px; text-align: center;">
      </el-pagination>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { defineProps } from 'vue';
import axios from 'axios';
import { ElMessage, ElMessageBox } from 'element-plus';

const props = defineProps<{ ServerID: number }>();

const tableData = ref<any[]>([]);
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const loading = ref(false);

const fetchServerLogData = async (page: number) => {
  if (page < 1) return;

  loading.value = true;

  try {
    const response = await axios.get(`/log/${props.ServerID}/`, {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      },
      params: {
        page: page,
        page_size: pageSize.value
      }
    });

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
  } finally {
    loading.value = false;
  }
};

const handlePageChange = (page: number) => {
  fetchServerLogData(page);
};

const handleDelete = async (logId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条日志记录吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    
    loading.value = true;
    await axios.delete(`/log/${props.ServerID}/${logId}/`, {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    });
    ElMessage.success(`从服务器删除log:${logId} 成功`)
    await fetchServerLogData(currentPage.value);
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败：' + (e as Error).message);
    }
  } finally {
    loading.value = false;
  }
};

const handleDownload = async (logId: number) => {
  try {
    const response = await axios.get(`/log/${props.ServerID}/${logId}/download/`, {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      },
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `log_${logId}.txt`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (e) {
    console.error(e);
  }
};

onMounted(() => {
  fetchServerLogData(currentPage.value);
});
</script>

<style scoped>
.el-table {
  margin-bottom: 20px;
}
</style>
  