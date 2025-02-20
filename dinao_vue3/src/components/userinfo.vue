<template>
  <div class="common-layout">
    <el-container>
      <!-- 主体内容 -->
      <el-main class="main">
        <div>
          <span>邮箱&nbsp;&nbsp;&nbsp;：</span>
          <el-input 
            v-model="email"
            style="width: 240px"
            type="email"
            placeholder="Enter your email"
            :suffix-icon="Message"  
          />
        </div>
        <div>
          <span>新邮箱&nbsp;：</span>
          <el-input 
            v-model="newemail"
            style="width: 240px;"
            type="email"
            placeholder="Enter your new email"
            :suffix-icon="Message"  
          />
        </div>
        <div>
          <span>新密码：</span>
          <el-input 
            v-model="password"
            style="width: 240px;"
            type="password"
            placeholder="Enter your password"
            :suffix-icon="Lock"  
          />
        </div>
        <div>
          <span>验证码：</span>
          <el-input 
            v-model="captcha"
            style="width: 160px;"
            placeholder="Enter your captcha"
            :suffix-icon="Refresh"  
          />
          <el-button style="width: 80px;" @click="getCaptcha">获取验证码</el-button>
        </div>
        <el-button style="width: 150px;" @click="Revise_email">修改邮箱</el-button>
        <el-button style="width: 150px;" @click="Revise_password">修改密码</el-button>
        <el-divider style="background-color: #2c3e50;" />
        <el-table :data="servers" style="width: 100%" max-height="250">
          <el-table-column fixed prop="formatted_created_at" label="创建日期" width="200" />
          <el-table-column prop="name" label="服务器" width="120" />
          <el-table-column prop="status" label="状态" width="120" />
          <el-table-column prop="ip_address" label="IP" width="150" />
          <el-table-column prop="port" label="端口号" width="120" />
          <el-table-column prop="operating_system" label="操作系统" width="120" />
          <el-table-column prop="user" label="用户" width="120" />
          <el-table-column fixed="right" label="操作" min-width="120">
            <template #default="scope">
              <el-button link type="primary" size="small" @click.prevent="deleteRow(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button class="mt-4" style="width: 100%" @click="showAlert">添加服务器</el-button>
      </el-main>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import {
  Refresh,
  Message,
  Lock,
} from '@element-plus/icons-vue'
import { onMounted } from 'vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router';
import axios from 'axios';

// 主体内容
import Swal from 'sweetalert2' // 导入第三方弹窗库sweetalert2
const email = ref('')
const newemail = ref('')
const password = ref('')
const captcha = ref('')

const Revise_email = async () => {
  // 邮箱修改
  axios.post('http://127.0.0.1:8000/api/email_verify/', {action: 'stopemail'});
  if (!email.value && !newemail.value) {
    console.log('邮箱不能为空');
    return;
  } else if (!captcha.value) {
    console.log('请输入验证码!');
    return;
  }
  try {
    const response = await axios.post ('http://127.0.0.1:8000/api/revise_email/', {
      email: email.value,
      newemail: newemail.value,
      captcha: captcha.value,
    });
    const success = response.data.message
    if (success === '操作成功' && response.status === 201) {
      alert('修改成功')
    }
  } catch (error){
    if (axios.isAxiosError(error)&&error.response){
      if (error.response.status === 444) {
        if (error.response.data.error === '验证码错误') {
          alert('请输入正确的邮箱!')
        } else if (error.response.data.error === '原始密码错误') {
          alert('请输入正确的验证码!')
        }
      }
    }
  };
}

const Revise_password = async () => {
  // 密码修改
  console.log('开始修改密码')
  axios.post('http://127.0.0.1:8000/api/email_verify/', {action: 'stopemail'});
  if (!password.value) {
    console.log('Revise_password', email.value);
    return;
  } else if (!captcha.value) {
    console.log('请输入验证码!');
    return;
  }
  try {
    const response = await axios.post ('http://127.0.0.1:8000/api/revise_password/', {
      password: password.value,
      email: email.value,
      captcha: captcha.value,
    });
    console.log('开始修改密码')
    const success = response.data.message
    if (success === '操作成功' && response.status === 201) {
      alert('修改成功')
    }
  } catch (error){
    if (axios.isAxiosError(error)&&error.response){
      if (error.response.status === 444) {
        if (error.response.data.error === '原始密码错误') {
          alert('原始密码错误，请输入正确的密码!')
        } else if (error.response.data.error === '验证码错误') {
          alert('验证码错误,请输入正确的验证码!')
        }
      }
    }
  };
}

// 获取验证码
const getCaptcha = async () => {
  if (!email.value) {
    console.log("邮箱不能为空:", email.value);
    return;
  }
  try {
    const response = await axios.post ('http://127.0.0.1:8000/api/email_verify/', {
      email: email.value,
      action: 'revise_get_code',
    });
    const success = response.data.success
    if (success === '操作成功' && response.status === 201) {
      alert('验证码发送成功，请查收!')
    }
  } catch (error) {
    if (axios.isAxiosError(error)&&error.response){
      if (error.response.status === 444) {
        if (error.response.data.error === '请输入正确的邮箱') {
          alert('请输入正确的邮箱!')
        } else if (error.response.data.error === '邮箱不存在') {
          alert('邮箱不存在,请重新输入!')
        }
      }
    }
  };
}

// 获取当前用户的所有服务器信息
import { useServerStore } from '../stores/serverdata';
import { computed } from 'vue'
const serverStore = useServerStore()
// 获取服务器数据
onMounted( async () => {
  await serverStore.fetchServers();
});
const servers = computed(() => serverStore.servers);
// 删除行函数
const deleteRow = async (index: number) => {
  const serverId = servers.value[index].id;
  try {
    await axios.delete(`/servers/${serverId}/`, {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    });
    servers.value.splice(index, 1);
  } catch (error) {
    console.error('删除服务器信息失败:', error);
  }
};

// 添加服务器弹窗
import { createApp } from 'vue';
import ServerInfoForm from './Serverfrom_data.vue';
import { useFormStore } from '../stores/Serverfrom_data';
import { createPinia } from 'pinia';
const showAlert = async () => {
  const formStore = useFormStore();
  Swal.fire({
    title: '输入服务器信息',
    html: '<div id="serverInfoForm"></div>',
    showCancelButton: true,
    confirmButtonText: '确认',
    didOpen: () => {
      const serverInfoFormContainer = document.getElementById('serverInfoForm');
      if (serverInfoFormContainer) {
        const formApp = createApp(ServerInfoForm);
        // 写入Pinia状态管理
        formApp.use(createPinia())
        // Mount Vue app
        formApp.mount(serverInfoFormContainer);
      }
    },
    preConfirm: () => {
      const formContainer = Swal.getPopup().querySelector('#serverInfoForm');
      if (formContainer) {
        const inputs = formContainer.querySelectorAll('input');
        return {
          name: inputs[0].value,
          ip_address: inputs[1].value,
          port: inputs[2].value,
          operating_system: inputs[3].value,
          status: 'active',
          user: inputs[4].value,
          password: inputs[5].value,
        };
      }
      return {};
    },
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        console.log('提交服务器信息：' + result.value);
        await axios.post('/servers/', result.value, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
        });
        Swal.fire('成功', '数据已提交', 'success');
        formStore.resetForm(); // 提交成功后重置表单
        // fetchServerData(); // 刷新服务器信息
        serverStore.fetchServers();
      } catch (error) {
        console.error(error);
        Swal.fire('错误', '数据提交失败', 'error');
      }
    }
  });
};
</script>

<!-- 样式 -->
<style>
  /* 主体布局 */
  .main {
    padding: 20px;
  }
</style>