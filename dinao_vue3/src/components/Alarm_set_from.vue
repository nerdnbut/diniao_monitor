<template>
  <div>
    <!-- 添加刷新控制区域 -->
    <div class="refresh-control">
      <el-switch
        v-model="autoRefresh"
        active-text="自动刷新"
        inactive-text="手动刷新"
      />
      <el-select v-if="autoRefresh" v-model="refreshInterval" class="refresh-interval">
        <el-option label="30秒" :value="30" />
        <el-option label="1分钟" :value="60" />
        <el-option label="2分钟" :value="120" />
        <el-option label="5分钟" :value="300" />
      </el-select>
      <el-button v-if="!autoRefresh" type="primary" @click="fetchAlarms">刷新</el-button>
    </div>

    <!-- 表格展示报警任务 -->
    <el-table :data="alarms" style="width: 100%" max-height="250">
      <el-table-column prop="name" label="服务器" width="150" />
      <el-table-column prop="alarmType" label="报警类型" width="150" />
      <el-table-column prop="alarmLevel" label="报警级别" width="150" />
      <el-table-column prop="threshold" label="阈值" width="120" />
      <el-table-column prop="current_value" label="当前值" width="120" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column fixed="right" label="操作" min-width="150">
        <template #default="scope">
          <!-- 删除按钮 -->
          <el-button type="danger" size="small" @click="deleteAlarm(scope.row.id)">删除</el-button>
          <!-- 修改按钮 -->
          <el-button type="primary" size="small" @click="showAlertForAlarm(scope.row)">修改</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import AlarmForm from './AlarmForm.vue'; // 引入 AlarmForm 组件
import { ref, onMounted, onUnmounted, watch } from 'vue';
import axios from 'axios';
import { ElTable, ElTableColumn, ElButton, ElSwitch, ElSelect, ElOption } from 'element-plus';
import Swal from 'sweetalert2'; // 弹窗库
// import { useFormStore } from '../stores/alarmTask_form' // Pinia Store
import { createApp } from 'vue';
import { createPinia } from 'pinia';

const alarms = ref([]);  // 存放报警任务的数据
const autoRefresh = ref(false);
const refreshInterval = ref(60);
let refreshTimer: number | null = null;

// 获取报警任务数据
const fetchAlarms = async () => {
  console.log('刷新')
  try {
    const response = await axios.get('/alarms/', {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    });
    alarms.value = response.data;
    console.log("Fetched alarms:", response.data);
  } catch (error) {
    console.error("Error fetching alarms:", error);
  }
};

// 设置定时刷新
const setupAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
  if (autoRefresh.value) {
    refreshTimer = window.setInterval(() => {
      fetchAlarms();
    }, refreshInterval.value * 1000);
  }
};

// 监听自动刷新开关变化
watch(autoRefresh, (newVal) => {
  if (newVal) {
    setupAutoRefresh();
  } else if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
});

// 监听刷新间隔变化
watch(refreshInterval, () => {
  if (autoRefresh.value) {
    setupAutoRefresh();
  }
});

// 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
});

// 删除报警任务
const deleteAlarm = async (id: number) => {
  try {
    await axios.delete(`/alarms/delete/${id}/`, {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    });
    fetchAlarms();  // 删除后重新加载数据
  } catch (error) {
    console.error("Error deleting alarm:", error);
  }
};

// 显示修改报警任务弹窗
// 显示修改报警任务弹窗
const showAlertForAlarm = async (alarm) => {
  const selectedAlarm = { ...alarm }; // 复制传入的报警任务数据
  let formInstance: any = null; // 保存子组件实例

  Swal.fire({
    title: '修改报警任务信息',
    html: '<div id="alarmInfoForm"></div>',  // 用于挂载报警任务表单
    showCancelButton: true,
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    didOpen: () => {
      const alarmInfoFormContainer = document.getElementById('alarmInfoForm');
      if (alarmInfoFormContainer) {
        const formApp = createApp(AlarmForm, {
          selectedAlarm: selectedAlarm,  // 把报警任务数据传递给 AlarmForm 组件
        });

        // 挂载 Vue 表单应用
        formApp.use(createPinia());
        formInstance = formApp.mount(alarmInfoFormContainer);
      }
    },
    preConfirm: () => {
      // 获取修改后的数据
      const formContainer = Swal.getPopup().querySelector('#alarmInfoForm');
      if (formContainer) {
        const inputs = formContainer.querySelectorAll('input, select');
        return {
          id: selectedAlarm.id,  // 传递报警任务ID
          threshold: inputs[0].value,  // 阈值
          alarmLevel: formInstance.localAlarm.alarmLevel,  // 报警级别
        };
      }
      return {};
    },
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        console.log('修改报警任务数据：', result.value);
        // 使用axios发送请求，更新报警任务
        await axios.patch(`/alarms/update/${result.value.id}/`, result.value, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
        });
        Swal.fire('成功', '报警任务已更新', 'success');
        // 刷新数据
        fetchAlarms();
      } catch (error) {
        console.error('更新报警任务失败:', error);
        Swal.fire('错误', '数据提交失败', 'error');
      }
    }
  });
};

// 加载报警任务
onMounted(fetchAlarms);
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}

.refresh-control {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.refresh-interval {
  width: 120px;
}
</style>