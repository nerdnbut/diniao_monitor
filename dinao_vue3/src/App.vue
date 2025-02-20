<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script lang="ts" setup>
//  import Login from "./views/Login.vue";
//  import Register from "./views/Register.vue";
</script>

<style scoped lang="scss">
/* 全局样式定义 */
#app {
  text-align: center;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 0;
  padding: 0;
}

body {
  margin: 0;
  padding: 0;
  font-family: Avenir, Helvetica, Arial, sans-serif;
}

html, body, #app {
  height: 100%;
}
</style>
