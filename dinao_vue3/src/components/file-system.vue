<template>
  <el-container>
    <!-- 服务器选择 -->
    <el-header style="padding: 20px 0;">
      <el-select 
        v-model="selectedServer" 
        placeholder="请选择服务器" 
        @change="handleServerChange"
        style="width: 300px;"
      >
        <el-option 
          v-for="server in servers" 
          :key="server.id" 
          :label="`${server.name} (${server.ip_address})`" 
          :value="server.id"
        />
      </el-select>
      <el-button type="primary" @click="refreshDirectory" style="margin-left: 10px;">刷新</el-button>
    </el-header>

    <!-- 文件系统主体 -->
    <template v-if="selectedServer">
      <el-container>
        <!-- 左侧目录树 -->
        <el-aside width="250px" style="border-right: 1px solid #dcdfe6; padding: 20px;">
          <el-tree
            ref="fileTreeRef"
            :data="treeData"
            :props="defaultProps"
            @node-click="handleNodeClick"
            node-key="path"
            :load="loadNode"
            lazy
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <el-icon><Folder v-if="data.type === 'directory'" /><Document v-else /></el-icon>
                <span>{{ node.label }}</span>
              </span>
            </template>
          </el-tree>
        </el-aside>

        <!-- 右侧文件列表 -->
        <el-main>
          <!-- 工具栏 -->
          <div class="toolbar">
            <el-upload
              :action="uploadUrl"
              :headers="headers"
              :data="uploadData"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :show-file-list="false"
            >
              <el-button type="primary">
                <el-icon><Upload /></el-icon>上传文件
              </el-button>
            </el-upload>
          </div>

          <!-- 文件列表 -->
          <el-table :data="fileList" style="width: 100%" v-loading="loading">
            <el-table-column label="文件名" min-width="200">
              <template #default="{ row }">
                <el-icon><Folder v-if="row.type === 'directory'" /><Document v-else /></el-icon>
                <span style="margin-left: 8px">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="大小" width="120">
              <template #default="{ row }">
                {{ formatFileSize(row.size) }}
              </template>
            </el-table-column>
            <el-table-column prop="modifiedTime" label="修改时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.modifiedTime) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button-group v-if="row.type === 'file'">
                  <el-button link @click="handleEdit(row)">编辑</el-button>
                  <el-button link @click="handleDownload(row)">下载</el-button>
                  <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
        </el-main>
      </el-container>

      <!-- 文件编辑对话框 -->
      <el-dialog
        v-model="editDialogVisible"
        :title="currentFile ? `编辑文件: ${currentFile.name}` : '编辑文件'"
        width="80%"
      >
        <el-input
          v-model="editContent"
          type="textarea"
          :rows="20"
          :loading="loading"
        />
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveFile">保存</el-button>
        </template>
      </el-dialog>
    </template>

    <!-- 未选择服务器时的提示 -->
    <el-empty v-else description="请先选择一个服务器" />
  </el-container>
</template>

<script>
import { Document, Folder, Upload } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'FileSystem',
  
  components: {
    Document,
    Folder,
    Upload
  },

  data() {
    return {
      servers: [],
      selectedServer: null,
      currentPath: '/',
      treeData: [],
      fileList: [],
      loading: false,
      editDialogVisible: false,
      editContent: '',
      currentFile: null,
      defaultProps: {
        children: 'children',
        label: 'name',
        isLeaf: 'isLeaf'
      }
    }
  },

  computed: {
    headers() {
      return {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    },

    uploadUrl() {
      return this.selectedServer ? `http://127.0.0.1:8000/api/servers/${this.selectedServer}/files/upload/` : ''
    },

    uploadData() {
      return {
        path: this.currentPath
      }
    }
  },

  created() {
    this.fetchServers()
  },

  methods: {
    // 获取服务器列表
    async fetchServers() {
      try {
        const response = await axios.get('/servers/', {
          headers: this.headers
        })
        this.servers = response.data.results
      } catch (error) {
        ElMessage.error('获取服务器列表失败')
      }
    },

    // 处理服务器切换
    handleServerChange(serverId) {
      this.currentPath = '/'
      this.fileList = []
      this.loadNode({ level: 0 }, () => {})
    },

    // 加载目录树节点
    async loadNode(node, resolve) {
      if (!this.selectedServer) {
        resolve([])
        return
      }

      try {
        this.loading = true
        const path = node.level === 0 ? '/' : node.data.path
        const response = await axios.get(`/servers/${this.selectedServer}/files/list/`, {
          params: { path },
          headers: this.headers
        })

        const files = response.data || []
        // 右侧只显示文件，左侧树形结构显示目录
        this.fileList = files.filter(f => f.type === 'file')
        resolve(files.filter(f => f.type === 'directory'))
        console.log(this.currentPath);
      } catch (error) {
        ElMessage.error('加载文件列表失败')
        resolve([])
      } finally {
        this.loading = false
      }
    },

    // 处理节点点击
    handleNodeClick(data) {
      this.currentPath = data.path
      this.loadNode({ data, level: 1 }, () => {})
    },

    // 处理文件编辑
    async handleEdit(file) {
      try {
        this.loading = true
        const response = await axios.get(`/servers/${this.selectedServer}/files/content/`, {
          params: { path: file.path },
          headers: this.headers
        })
        this.editContent = response.data.content
        this.currentFile = file
        this.editDialogVisible = true
      } catch (error) {
        ElMessage.error('获取文件内容失败')
      } finally {
        this.loading = false
      }
    },

    // 保存文件
    async saveFile() {
      try {
        this.loading = true
        await axios.post(`/servers/${this.selectedServer}/files/save/`, {
          path: this.currentFile.path,
          content: this.editContent
        }, {
          headers: this.headers
        })
        this.editDialogVisible = false
        ElMessage.success('保存成功')
      } catch (error) {
        ElMessage.error('保存失败')
      } finally {
        this.loading = false
      }
    },

    // 处理文件下载
    async handleDownload(file) {
      try {
        const response = await axios.get(`/servers/${this.selectedServer}/files/download/`, {
          params: { path: file.path },
          headers: this.headers,
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.download = file.name
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        ElMessage.error('下载失败')
      }
    },

    // 处理文件删除
    async handleDelete(file) {
      try {
        await ElMessageBox.confirm(`确定要删除 ${file.name} 吗？`, '警告', {
          type: 'warning'
        })
        
        await axios.delete(`/servers/${this.selectedServer}/files/delete/`, {
          params: { path: file.path },
          headers: this.headers
        })
        
        ElMessage.success('删除成功')
        this.loadNode({ data: { path: this.currentPath }, level: 1 }, () => {})
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    },

    // 处理文件上传成功
    handleUploadSuccess() {
      ElMessage.success('上传成功')
      this.loadNode({ data: { path: this.currentPath }, level: 1 }, () => {})
    },

    // 处理文件上传失败
    handleUploadError() {
      ElMessage.error('上传失败')
    },

    // 格式化文件大小
    formatFileSize(size) {
      const units = ['B', 'KB', 'MB', 'GB']
      let index = 0
      while (size > 1024 && index < units.length - 1) {
        size /= 1024
        index++
      }
      return `${size.toFixed(2)} ${units[index]}`
    },

    // 格式化日期
    formatDate(timestamp) {
      return new Date(timestamp * 1000).toLocaleString()
    },

    // 刷新目录
    refreshDirectory() {
      this.loadNode({ data: { path: this.currentPath }, level: 1 }, () => {});
    }
  }
}
</script>

<style scoped>
.toolbar {
  margin-bottom: 20px;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.el-icon {
  margin-right: 4px;
}

.el-header {
  border-bottom: 1px solid #dcdfe6;
}
</style>