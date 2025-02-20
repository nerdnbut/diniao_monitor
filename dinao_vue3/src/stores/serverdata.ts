import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import dayjs from 'dayjs';

const tableData = ref([]);

export const useServerStore = defineStore('server', {
  state: () => ({
    servers: []
  }),
  actions: {
    async fetchServers() {
      try {
        const response = await axios.get('/servers/', {
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        });
        // 格式化日期
        tableData.value = response.data.results.map((server: any) => ({
            ...server,
            formatted_created_at: dayjs(server.created_at).format('YYYY/MM/DD HH:mm'),
            formatted_updated_at: dayjs(server.updated_at).format('YYYY/MM/DD HH:mm'),
        }));
        if (response.status === 200) {
          this.servers = tableData.value
        }
      } catch (error) {
        console.error('获取数据失败:', error);
      }
    }
  }
});
