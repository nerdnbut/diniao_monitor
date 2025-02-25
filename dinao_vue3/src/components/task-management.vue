<template>
  <el-container>
    <el-header>
      <el-button type="primary" @click="showCreateTaskDialog">创建任务</el-button>
    </el-header>

    <el-main>
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="schedule" label="调度时间" />
        <el-table-column prop="status" label="状态" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button @click="editTask(row)">编辑</el-button>
            <el-button type="danger" @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-main>

    <el-dialog title="创建任务" v-model.sync="createTaskDialogVisible">
      <el-form :model="newTask">
        <el-form-item label="任务名称">
          <el-input v-model="newTask.name" />
        </el-form-item>
        <el-form-item label="调度时间">
          <el-input v-model="newTask.schedule" placeholder="例如：0 0 * * *" />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="newTask.type">
            <el-option label="备份" value="backup" />
            <el-option label="重启服务" value="restart" />
            <el-option label="执行脚本" value="script" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTask">创建</el-button>
        <el-button @click="createTaskDialogVisible = false">取消</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script>
import axios from 'axios';
import { ElMessage } from 'element-plus';

export default {
  data() {
    return {
      tasks: [],
      createTaskDialogVisible: false,
      newTask: {
        name: '',
        schedule: '',
        type: ''
      }
    };
  },
  methods: {
    fetchTasks() {
      // 获取任务列表
      axios.get('/api/tasks/')
        .then(response => {
          this.tasks = response.data;
        })
        .catch(error => {
          ElMessage.error('获取任务列表失败');
        });
    },
    showCreateTaskDialog() {
      this.createTaskDialogVisible = true;
    },
    createTask() {
      // 创建新任务
      axios.post('/api/tasks/', this.newTask)
        .then(response => {
          this.tasks.push(response.data);
          this.createTaskDialogVisible = false;
          ElMessage.success('任务创建成功');
          this.newTask = { name: '', schedule: '', type: '' }; // 重置表单
        })
        .catch(error => {
          ElMessage.error('创建任务失败');
        });
    },
    editTask(task) {
      // 编辑任务逻辑
      console.log('编辑任务:', task);
    },
    deleteTask(task) {
      // 删除任务逻辑
      axios.delete(`/api/tasks/${task.id}/`)
        .then(() => {
          this.tasks = this.tasks.filter(t => t.id !== task.id);
          ElMessage.success('任务删除成功');
        })
        .catch(error => {
          ElMessage.error('删除任务失败');
        });
    }
  },
  created() {
    this.fetchTasks();
  }
};
</script>

<style scoped>
/* 添加样式 */
</style>