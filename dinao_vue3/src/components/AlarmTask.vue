<template>
    <div class="alarm-task-setting">
      <el-form :model="form" label-width="120px" class="form" ref="formRef" :rules="rules" @submit.native.prevent>
        <!-- 选择服务器 -->
        <el-form-item label="选择服务器" prop="serverId">
          <el-select v-model="form.serverId" placeholder="请选择服务器">
            <el-option v-for="server in servers" :key="server.id" :label="server.name" :value="server.id" />
          </el-select>
        </el-form-item>
  
        <!-- 报警类型 -->
        <el-form-item label="报警类型" prop="alarmType">
          <el-select v-model="form.alarmType" placeholder="请选择报警类型">
            <el-option label="CPU 使用率" value="cpu" />
            <el-option label="内存使用率" value="memory" />
            <el-option label="磁盘空间" value="disk" />
            <el-option label="网络带宽" value="network" />
          </el-select>
        </el-form-item>
  
        <!-- 报警级别 -->
        <el-form-item label="报警级别" prop="alarmLevel">
          <el-select v-model="form.alarmLevel" placeholder="请选择报警级别">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
  
        <!-- 阈值输入框 -->
        <el-form-item label="报警阈值" prop="threshold">
          <el-input v-model="form.threshold" placeholder="请输入阈值" />
        </el-form-item>
  
        <!-- 提交按钮 -->
        <el-form-item>
          <el-button @click="submitForm">提交</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </template>
  
  <script lang="ts" setup>
  import { reactive } from 'vue';
  import { ElMessage, ElForm, ElSelect, ElOption, ElInput, ElButton } from 'element-plus';
  import axios from 'axios';
  
  // 表单数据
  const form = reactive({
    serverId: '',
    alarmType: '',
    alarmLevel: '',
    threshold: '', // 默认空阈值
  });
  
  // 表单验证规则
  const rules = {
    serverId: [{ required: true, message: '请选择服务器', trigger: 'change' }],
    alarmType: [{ required: true, message: '请选择报警类型', trigger: 'change' }],
    alarmLevel: [{ required: true, message: '请选择报警级别', trigger: 'change' }],
    threshold: [{ required: true, message: '请输入阈值', trigger: 'blur' }],
  };

  interface Server {
    id: number;
    name: string;
  }

  // 状态变量
  const props = defineProps<{
    servers: Server[];
  }>(); // 服务器数据
  // const selectedServerName = ref<string>('选择服务器');
  // const handleCommand = async (serverId: number) => {
  // const selectedServer = props.servers.find(server => server.id === serverId);
  // if (selectedServer) {
  //   selectedServerName.value = selectedServer.name;  // 更新选中的服务器名称
  // }
  // };

  // 提交表单
  const submitForm = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/alarm-task/', form, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      ElMessage.success(response.data.message);
      // 成功提示
      ElMessage.success('创建报警任务成功');
    } catch (error) {
      ElMessage.error('创建报警任务失败');
    }
  };
  
  // 重置表单
  const resetForm = () => {
    form.serverId = '';
    form.alarmType = '';
    form.alarmLevel = '';
    form.threshold = ''; // 默认空阈值
  };
  </script>
  
  <style scoped>
  /* 按钮容器样式 */
  .el-form-item:last-child {
    display: flex;
    justify-content: space-between;
    margin-top: 30px;
    gap: 4%; /* 按钮间距 */
  }
  
  /* 按钮基础样式 */
  .el-button {
    flex: 1; /* 自动扩展剩余空间 */
    width: 100px !important; /* 实际宽度 = 50% - 间距的一半 */
    height: 30px !important; /* 输入框默认高度40px，设置为50% */
    padding: 0 12px !important; /* 缩小内边距 */
    font-size: 12px !important; /* 调整字体大小 */
    text-align: center; /* 文字居中 */
    font-size: 14px; /* 字体大小 */
  }
  
  /* 其他原有样式保持不变 */
  .alarm-task-setting {
    max-width: 500px;
    margin: 0 auto;
    padding: 30px;
    background-color: #f4f4f4;
    border-radius: 10px;
  }
  
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .el-input,
  .el-select {
    border-radius: 5px;
  }
  
  .el-form {
    padding: 20px;
  }
  </style>