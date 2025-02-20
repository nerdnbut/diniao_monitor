<template>
  <div class="login-container">
    <div class="pixel-chicken" @click="handleChickenClick"></div>
    <div class="login-form">
      <h2>Login</h2>
      <input v-model="username" type="text" placeholder="email" class="input-field" @keyup.enter="handleLoginClick" />
      <input v-model="password" type="password" placeholder="Password" class="input-field" @keyup.enter="handleLoginClick" />
      <button class="login-button" @click="handleLoginClick">登录</button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <p>没有账号? <span @click="handleChickenClick">注册</span></p>
    </div>
  </div>
</template>


<script lang="ts" setup name="Login">
import Swal from 'sweetalert2';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
axios.defaults.withCredentials = true

const router = useRouter();
const errorMessage = ref('');
const username = ref('');
const password = ref('');

const handleChickenClick = () => {
  // 点击小鸡后跳转到注册界面
  router.push('/register');
};
const setCookie = (name: string, value: string, days: number) => { let expires = ""; if (days) { const date = new Date(); date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000)); expires = "; expires=" + date.toUTCString(); } document.cookie = name + "=" + (value || "") + expires + "; path=/"; }
// 登录逻辑
const handleLoginClick = async () => {
  console.log('用户名与密码:', username.value, password.value);
  if (!username.value) {
    errorMessage.value = '用户名不能为空';
    return;
  } else if (!password.value) {
    errorMessage.value = '密码不能为空';
    return;
  }
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/login/', {
      username: username.value,
      password: password.value,
    }, {
    withCredentials: true
  });
    if (response.status === 200) {
      setCookie('token', response.data.token, 1)
      errorMessage.value = '';
      // 保存 token
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('username', response.data.username);
      router.push('/diniao'); // 登录成功后跳转到主页
      Swal.fire({
        title: true,
        position: 'top-end',
        timer: 1800,
        titleText: '登录成功!',
        width: '13%',
        showConfirmButton: false,
        icon: 'success',
        customClass: {
          popup: 'custom-popup',
        }
      })
    }
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 444) {
        if (error.response.data.error === '密码错误') {
          errorMessage.value = '密码错误!';
        } else if (error.response.data.error === '用户名不存在') {
          errorMessage.value = '该用户不存在!';
        }
      }
    }
  }
};

</script>

<style scoped lang="scss">
.error-message {
  color: red;
  margin-top: 5px;
}

.input-field {
  width: 80%;
  margin-bottom: 20px;
  padding: 10px;
  border: none;
  border-radius: 5px;
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
}
.login-button {
  width: 80%;
  padding: 10px;
  border: none;
  border-radius: 20px;
  background-color: #fff;
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f0f0f0;
}

.pixel-chicken {
  width: 50px;
  height: 50px;
  background-image: url('/path-to-pixel-chicken.png');
  background-size: contain;
  cursor: pointer;
  animation: walk 2s infinite linear;
}

@keyframes walk {
  0% { transform: translateX(-10px); }
  50% { transform: translateX(10px); }
  100% { transform: translateX(-10px); }
}

.custom-popup {
  height: 200px; /* 设置弹窗的高度 */
}

</style>
