<template>
  <div>
    <h2>创建定时任务</h2>
    <!-- 创建任务和刷新按钮 -->
    <el-button type="primary" @click="showCreateTaskForm">创建任务</el-button>
    <el-button @click="fetchTasks">刷新任务列表</el-button>

    <!-- 任务列表 -->
    <el-table :data="tasks" style="margin-top: 20px;">
      <el-table-column prop="server" label="服务器" />
      <el-table-column prop="script_type" label="脚本类型" />
      <el-table-column prop="execute_time" label="执行时间" />
      <!-- <el-table-column prop="execute_count" label="执行次数" /> -->
      <el-table-column prop="is_recurring" label="循环执行" />
      <el-table-column label="操作">
        <template v-slot="scope">
          <el-button type="danger" @click="deleteTask(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建任务表单 -->
    <el-dialog v-model="isCreateTaskDialogVisible" title="创建定时任务">
      <el-form @submit.prevent="createTask" label-width="120px">
        <!-- 选择服务器 -->
        <el-form-item label="部署至的服务器" :rules="[{ required: true, message: '请选择服务器', trigger: 'change' }]">
          <el-select v-model="task.serverId" placeholder="请选择服务器" required>
            <el-option v-for="server in servers" :key="server.id" :value="server.id" :label="server.name" />
          </el-select>
        </el-form-item>

        <!-- 上传脚本 -->
        <el-form-item label="上传脚本" :rules="[{ required: true, message: '请上传脚本', trigger: 'change' }]">
          <el-upload
            ref="upload"
            class="upload-demo"
            drag
            :headers="headers"
            :action="uploadUrl"
            :on-change="handleFileChange"
            :show-file-list="true"
            :on-exceed="onExceed"
            :on-success="uploadSuccess"
            limit="1"
            accept=".py,.sh" 
            :rules="[{ required: true, message: '请上传脚本', trigger: 'change' }]">
            <el-button>点击或拖拽文件到这里上传</el-button>
          </el-upload>
        </el-form-item>

        <!-- 脚本类型 -->
        <el-form-item label="脚本类型" :rules="[{ required: true, message: '请选择脚本类型', trigger: 'change' }]">
          <el-select v-model="task.scriptType" placeholder="请选择脚本类型" required>
            <el-option label="Python" value="python" />
            <el-option label="Shell" value="shell" />
          </el-select>
        </el-form-item>

        <!-- 执行时间 -->
        <el-form-item label="执行时间" :rules="[{ required: true, message: '请选择执行时间', trigger: 'change' }]">
          <el-time-picker v-model="task.executeTime" placeholder="选择执行时间" required />
        </el-form-item>

        <!-- 是否循环执行 -->
        <el-form-item label="循环执行">
          <el-switch v-model="task.isRecurring" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" native-type="submit">创建任务</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import { ElMessage } from 'element-plus';

export default {
  data() {
    return {
      task: {
        serverId: null,
        scriptFile: null,
        scriptType: 'python',
        executeTime: '',
        // executeCount: 1,
        isRecurring: false,
      },
      servers: [],  // 服务器列表
      tasks: [],    // 已创建任务列表
      isCreateTaskDialogVisible: false, // 控制创建任务对话框的显示
    };
  },
  created() {
    this.fetchServers();  // 加载服务器列表
    this.fetchTasks();    // 加载已创建任务列表
  },
  computed: {
    headers() {
      return {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    },
    uploadUrl() {
      return 'http://127.0.0.1:8000/api/upload-script/'
    }
  },
  methods: {
    // 加载服务器列表
    async fetchServers() {
      try {
        const response = await axios.get('/servers/', {
          headers: this.headers
        });
        this.servers = response.data.results;
      } catch (error) {
        ElMessage.error('无法加载服务器:', error);
      }
    },

    // 加载已创建任务列表
    async fetchTasks() {
      try {
        const response = await axios.get('/tasks/', {
          headers: this.headers
        });
        this.tasks = response.data.map(task => ({
          ...task,
          execute_time: new Date(task.execute_time).toLocaleString('zh-Hans-CN', { timeZone: 'Asia/Shanghai' }) // 转换为北京时间
        }));
      } catch (error) {
        ElMessage.error('无法加载任务列表:', error);
      }
    },

    // 显示创建任务表单
    showCreateTaskForm() {
      this.isCreateTaskDialogVisible = true;
    },

    // 处理文件上传
    handleFileChange(event) {
      this.task.scriptFile = event.raw;
    },
    onExceed() {
      ElMessage.warning('一次只能上传一个脚本')
    },
    uploadSuccess(res) {
      ElMessage.success('脚本上传成功');
      this.task.scriptPath = res.script_path;
    },
    // 创建定时任务
    async createTask() {
      const formData = new FormData();
      formData.append('server_id', this.task.serverId);
      formData.append('file', this.task.scriptFile);
      formData.append('script_type', this.task.scriptType);
      // 直接传递用户输入的时间
      formData.append('execute_time', new Date(this.task.executeTime).toISOString());
      formData.append('is_recurring', this.task.isRecurring ? 'true' : 'false');
      formData.append('script_path', this.task.scriptPath);

      try {
        const response = await axios.post('/create-task/', formData, {
          headers: this.headers
        });
        ElMessage.success('任务创建成功');
        this.isCreateTaskDialogVisible = false;
        this.task = { 
          serverId: '',
          scriptFile: null,
          scriptType: '',
          executeTime: '',
          isRecurring: false,
          scriptPath: ''
        };
        this.$refs.upload.clearFiles();
        this.fetchTasks(); // 刷新任务列表
      } catch (error) {
        ElMessage.error('任务创建失败' + error);
      }
    },
    // 删除任务
    async deleteTask(taskId) {
      const confirmDelete = await ElMessageBox.confirm('确定要删除这个任务吗?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      });
      if (confirmDelete) {
        try {
          await axios.delete(`/tasks/${taskId}/`, {
            headers: this.headers
          });
          ElMessage.success('任务删除成功');
          this.fetchTasks(); // 刷新任务列表
        } catch (error) {
          ElMessage.error('删除任务失败:', error);
        }
      }
    }
  }
};
</script>
