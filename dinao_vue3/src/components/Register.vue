<template>
    <div class="register-container">
      <div class="egg">
        <form @submit.prevent="register">
          <input v-model="username" type="text" placeholder="Username" class="input-field" required />
          <span v-if="usernameError" class="error">{{ usernameError }}</span>

          <input v-model="email" type="email" placeholder="Email" class="input-field" required />
          <span v-if="emailError" class="error">{{ emailError }}</span>

          <!-- 接收验证码输入框 -->
          <input v-model="captcha" type="text" placeholder="Captcha" class="input-captcha" required />
          <button @click="sendCaptcha"type="button" class="captcha-button">发送</button>
  
          <input v-model="password" type="password" placeholder="Password" class="input-field" required />
          <span v-if="passwordError" class="error">{{ passwordError }}</span>
  
          <input v-model="confirmPassword" type="password" placeholder="Confirm Password" class="input-field" required />
          <span v-if="confirmPasswordError" class="error">{{ confirmPasswordError }}</span>
  
          <button type="submit" class="register-button">Register</button>
          <button @click="cancel" class="cancel-button">Cancel</button>
        </form>
      </div>
    </div>
</template>
  
<script lang="ts" setup name="Register">
    import { ref } from 'vue';
    import axios from 'axios';
    import { useRouter } from 'vue-router';
    
    const username = ref('');
    const email = ref('');
    const captcha = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    
    const usernameError = ref('');
    const emailError = ref('');
    const passwordError = ref('');
    const confirmPasswordError = ref('');
    
    const router = useRouter();
    
    const register = async () => {
        // 重置错误信息
    usernameError.value = '';
    emailError.value = '';
    passwordError.value = '';
    confirmPasswordError.value = '';

    // 验证用户名和密码
    if (!username.value) {
        usernameError.value = '用户名不能为空。';
        return;
    }
    
    if (!email.value) {
        emailError.value = '邮箱不能为空。';
        return;
    }
    
    if (!captcha.value) {
        emailError.value = '验证码不能为空。';
        return;
    }

    if (password.value !== confirmPassword.value) {
        confirmPasswordError.value = '两次输入的密码不一致。';
        return;
    }

    if (!password.value) {
        passwordError.value = '密码不能为空。';
        return;
    } else if (!isPasswordStrong(password.value)) {
        passwordError.value = '密码过于简单。';
        return;
    }

    // 发送注册请求
    try {
        const response = await axios.post('http://127.0.0.1:8000/api/register/', {
            username: username.value,
            email: email.value,
            captcha: captcha.value,
            password: password.value,
        }, { withCredentials: true });
        alert(response.data.message);
        router.push('/login');
    } catch (error) {
            // 检查 error 是否为 AxiosError 类型
            if (axios.isAxiosError(error) && error.response) { 
                // 打印eroor信息
            if (error.response.status === 400) {
                if (error.response.data.error === '用户名已存在') {
                    alert('用户名已存在。');
                } else {
                    alert(error.response?.data?.error || '发生一个错误');
                }
            } else if (error.response.status === 411) {
                if (error.response.data.error === '邮箱已存在') {
                    alert('邮箱已存在。');
                } else {
                    alert(error.response?.data?.error || '发生一个错误');
                }
            } else if (error.response.status === 422) {
                if (error.response.data.error === '请输入正确的邮箱') {
                    alert('请输入正确的邮箱！');
                } else {
                    alert(error.response?.data?.error || '发生一个错误');
                }
            } else if (error.response.status === 433) {
                if (error.response.data.error === '请先获取验证码') {
                    alert('验证码又错，请重新获取！');
                } else {
                    alert(error.response?.data?.error || '发生一个错误');
                }
            }
        } else {
            alert('未能连接到服务器，请稍后再试。');
        }
      }
      axios.post('http://127.0.0.1:8000/api/email_verify/', {action: 'stopemail'}), { withCredentials: true };
    };

    const cancel = () => {
    router.push('/login');
    };

    // 密码强度验证函数
    const isPasswordStrong = (password: string) => {
    // 这里是一个简单的密码强度验证逻辑，可以根据需求进行修改
    return password.length >= 8 && /\d/.test(password) && /[A-Z]/.test(password);
    };

    // 发送验证码
    const sendCaptcha = async () => {
        if (!email.value) {
        emailError.value = '邮箱不能为空。';
        return;
        }
        // 发送验证码请求
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/email_verify/', {
                email: email.value,
                action: 'runemail',
            }, { withCredentials: true });
            // alert(response.data.message);
            const success = response.data.success
            if (success === '操作成功' && response.status === 200) {
                alert('验证码已发送。')
            }
            // 输出验证码已发送
            console.log('验证码已发送：'+response.data.captcha);
        } catch (error) {
            if (axios.isAxiosError(error) && error.response) {
                if (error.response.status === 422) {
                    if (error.response.data.error === '请输入正确的邮箱') {
                        alert('请输入正确的邮箱！');
                }
            }
        }
    };}
</script>
  
<style scoped lang="scss" name="Register">
    .register-container {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background-color: #f0f0f0;
    }
    
    .egg {
        width: 500px;
        height: 600px;
        background-color: #fff;
        border-radius: 80%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
    }
    
    .input-field {
        width: 80%;
        margin-bottom: 20px;
        padding: 10px;
        border: none;
        border-radius: 5px;
        box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
    }

    .input-captcha {
        width: 70%;
        margin-bottom: 20px;
        padding: 10px;
        border: none;
        border-radius: 5px;
        box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
    }
    
    .error {
        color: red;
        font-size: 12px;
        margin-bottom: 15px;
        margin-top: 5px;
        display: block;
    }

    .register-button, .cancel-button {
        width: 80%;
        padding: 10px;
        border: none;
        border-radius: 20px;
        margin-bottom: 10px; 
        cursor: pointer;
    }

    .register-button {
        background-color: #fff;
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
    }

    .cancel-button {
        background-image: url('/path-to-pixel-poop.png');
        background-size: contain;
    }

    .captcha-button {
        padding: 10px;
        background-color: #fff;
        border-radius: 20px;
        margin-bottom: 10px;
        border: none; 
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
    }


</style>
  