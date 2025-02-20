<template>
  <el-container style="height: 100vh;">
    <el-header style="height: 10%; display: flex; align-items: center; justify-content: center;">
      服务器信息
    </el-header>

    <el-container>
      <el-aside style="width: 50%; display: flex; align-items: center; justify-content: center;">
        <div v-if="monitoringData && monitoringData.memoryUsage.length" class="demo-progress">
          <el-progress type="dashboard" :color="colors" :percentage="monitoringData.memoryUsage[0]" />
          <p>内存使用率: {{ monitoringData.memoryUsage[0] }}%</p>
        </div>
        <div v-if="monitoringData && monitoringData.swpUsage.length" class="demo-progress">
          <el-progress type="dashboard" :color="colors" :percentage="monitoringData.swpUsage[0]" />
          <p>SWAP 使用率: {{ monitoringData.swpUsage[0] }}%</p>
        </div>
        <div v-else>
          <p>加载中...</p>
        </div>
      </el-aside>

      <el-main>
        <div v-if="monitoringData">
          <div v-if="monitoringData.cpuUsage.length > 1" style="max-height: 200px; overflow-y: auto;">
            <div v-for="(usage, index) in monitoringData.cpuUsage.slice(1)" :key="index" class="cpu-bar">
              <span>CPU{{ index + 1 }} 使用率: {{ usage }}</span>
              <el-progress :text-inside="true" :stroke-width="24" :percentage="usage" status="success" />
            </div>
          </div>
        </div>
        <div v-else>
          <p>加载中...</p>
        </div>
      </el-main>
    </el-container>

    <el-container style="height: 50%;">
      <el-aside style="width: 50%; display: flex; align-items: center; justify-content: center;">
        <el-table v-if="monitoringData && monitoringData.disk.length" :data="monitoringData.disk" style="width: 100%">
          <el-table-column prop="Filesystem" label="Filesystem" />
          <el-table-column prop="Size" label="Size" />
          <el-table-column prop="Used" label="Used" />
          <el-table-column prop="Avail" label="Avail" />
          <el-table-column prop="Use%" label="Use%" />
          <el-table-column prop="Mounted" label="Mounted on" />
        </el-table>
        <div v-else>
          <p>加载中...</p>
        </div>
      </el-aside>

      <el-main style="width: 50%; display: flex; align-items: center; justify-content: center;">
        <div v-if="monitoringData" style="width: 100%; height: auto;">
          <el-main style="display: flex; align-items: center; justify-content: center;">
            <div ref="networkChart" style="width: 100%; height: 400px;"></div>
          </el-main>
        </div>
        <div v-else>
          <p>加载中...</p>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';
import * as echarts from 'echarts';

const colors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]

interface MonitoringData {
  cpuUsage: number[];
  memoryUsage: number[];
  swpUsage: number[];
  network: {
    interfaces: string[];
    rxRates: number[];
    txRates: number[];
  };
  disk: {
    Filesystem: string;
    Size: string;
    Used: string;
    Avail: string;
    'Use%': string;
    Mounted: string;
  }[];
}

const props = defineProps<{ serverId: number }>();
const monitoringData = ref<MonitoringData | null>(null);
const networkChart = ref<HTMLDivElement | null>(null);
let intervalId: number | undefined;

const fetchMonitoringData = async () => {
  try {
    const response = await axios.get(`/servers/${props.serverId}/monitor/`, {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    });
    const data = response.data;
    const cpuUsageData = (Object.values(JSON.parse(data.cpu)) as string[]).map(usage => parseFloat(usage.replace('%', '')));
    const networkData = data.network;
    const networkInterfaces = Object.keys(networkData);
    const rxRates = networkInterfaces.map(interfaceName => networkData[interfaceName].rx_rate);
    const txRates = networkInterfaces.map(interfaceName => networkData[interfaceName].tx_rate);

    monitoringData.value = {
      cpuUsage: cpuUsageData,
      memoryUsage: [parseFloat(data.mem.toFixed(2))],
      swpUsage: [parseFloat(data.swp.toFixed(2))],
      network: {
        interfaces: networkInterfaces,
        rxRates: rxRates,
        txRates: txRates
      },
      disk: data.disk
    };
  } catch (error) {
    console.error('获取监控数据失败', error);
  }
};

const updateNetworkChart = () => {
  if (!networkChart.value || !monitoringData.value || !monitoringData.value.network) return;

  const networkChartInstance = echarts.getInstanceByDom(networkChart.value) || echarts.init(networkChart.value);
  const option = {
    title: {
      text: 'Network Traffic',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      data: ['RX Rate', 'TX Rate'],
      top: '10%',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
    },
    yAxis: {
      type: 'category',
      data: monitoringData.value.network.interfaces,
    },
    series: [
      {
        name: 'RX Rate',
        type: 'bar',
        data: monitoringData.value.network.rxRates,
      },
      {
        name: 'TX Rate',
        type: 'bar',
        data: monitoringData.value.network.txRates,
      },
    ],
  };
  networkChartInstance.setOption(option);
};

onMounted(() => {
  fetchMonitoringData(); // 初次加载时获取数据
  intervalId = setInterval(fetchMonitoringData, 5000); // 每5秒获取一次数据

  watch(monitoringData, () => {
    updateNetworkChart();
  });
});

onBeforeUnmount(() => {
  if (intervalId) clearInterval(intervalId);  // 清除定时器
});
</script>

<style scoped>
/* 自定义样式 */
.demo-progress .el-progress {
  margin-bottom: 15px;
  max-width: 600px;
  margin-left: 20px; /* 增加左间隔 */
  margin-right: 20px; /* 增加右间隔 */
}
</style>
