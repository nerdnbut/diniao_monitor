<template>
  <form>
    <label for="name">名称:</label>
    <input class="input-field" type="text" id="name" v-model="name">
    <br>
    <label for="ip">IP&nbsp;&nbsp;:</label>
    <input class="input-field" type="text" id="ip" v-model="ip">
    <br>
    <label for="port">端口:</label>
    <input class="input-field" type="text" id="port" v-model="port">
    <br>
    <label for="os">OS&nbsp;&nbsp;:</label> 
    <input class="input-field" type="text" id="os" v-model="os">
    <br>
    <label for="os">用户:&nbsp;&nbsp;:</label>
    <input class="input-field" type="text" id="user" v-model="user">
    <br>
    <label for="password">密码:</label>
    <input class="input-password" :type="showPassword ? 'text' : 'password'" id="password" v-model="password">
    <Hide v-if="showPassword" style="width: 1em; height: 1em; margin-right: 10px" @click="togglePassword" />
    <View v-else style="width: 1em; height: 1em; margin-right: 10px" @click="togglePassword" />
  </form>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { View, Hide } from '@element-plus/icons-vue';
import { useFormStore } from '../stores/Serverfrom_data';

const showPassword = ref(false);
const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

// 引入store定义的Pinia状态管理
const formStore = useFormStore();

// 使用computed属性确保双向绑定
const name = computed({
  get: () => formStore.name,
  set: (value) => formStore.updateField('name', value),
});

const ip = computed({
  get: () => formStore.ip,
  set: (value) => formStore.updateField('ip', value),
});

const port = computed({
  get: () => formStore.port,
  set: (value) => formStore.updateField('port', value),
});

const os = computed({
  get: () => formStore.os,
  set: (value) => formStore.updateField('os', value),
});

const user = computed({
  get: () => formStore.user,
  set: (value) => formStore.updateField('user', value),
});


const password = computed({
  get: () => formStore.password,
  set: (value) => formStore.updateField('password', value),
});
</script>

<style scoped lang="scss">
.input-field {
  width: 80%;
  margin-bottom: 20px;
  padding: 10px;
  border: none;
  border-radius: 5px;
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
}

.input-password {
  width: 75%;
  margin-bottom: 20px;
  padding: 10px;
  border: none;
  border-radius: 5px;
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
}
</style>
