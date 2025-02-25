<template>
  <el-container>
    <el-main>
      <Loginformationdisplay v-if="serverlogdisplay" :ServerID="serverlogdisplay" />
      <el-skeleton :loading="loading" animated :count="servers.length">
        <template #default v-if="showServers">
          <el-row :gutter="20">
            <el-col :span="6" v-for="server in servers" :key="server.id">
              <el-card :body-style="{ padding: '0px', marginBottom: '10px' }">
                <img src="https://fuss10.elemecdn.com/0/6f/e35ff375812e6b0020b6b4e8f9583jpeg.jpeg" class="image" />
                <div style="padding: 8px">
                  <div class="info-item">
                    <label>名称：</label>
                    <span>{{ server.name }}</span>
                  </div>
                  <div class="info-item">
                    <label>IP地址：</label>
                    <span>{{ server.ip_address }}</span>
                  </div>
                  <div class="info-item">
                    <label>操作系统：</label>
                    <span>{{ server.operating_system }}</span>
                  </div>
                  <div class="info-item" style="margin-top: 5px">
                    <el-button type="primary" size="small" @click="hideServers(server.id)">查看日志</el-button>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </template>
      </el-skeleton>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import Loginformationdisplay from './Loginformationdisplay.vue';

interface Server {
  id: number,
  name: string,
  operating_system: string,
  ip_address: string
}

const servers = ref<Server[]>([]);
const loading = ref(true);
const showServers = ref(true);
const serverlogdisplay = ref<number | null>(null);

const fetchServers = async () => {
  try {
    loading.value = true;
    const response = await axios.get('/servers/', {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    });
    servers.value = response.data.results;
  } catch (error) {
    console.error('获取服务器列表失败:', error);
    ElMessage.error('获取服务器列表失败');
  } finally {
    loading.value = false;
  }
};

const setLoading = () => {
  fetchServers();
};

const hideServers = (id: number) => {
  showServers.value = false;
  serverlogdisplay.value = id;
};

onMounted(() => {
  fetchServers();
});
</script>

<style scoped>
.image {
  width: 100%;
  height: 120px; /* 固定图片高度 */
  object-fit: cover; /* 保持图片比例 */
}

.info-item {
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  font-size: 13px; /* 减小字体大小 */
}

.info-item label {
  font-weight: bold;
  margin-right: 4px;
  width: 60px;
}
</style>
  