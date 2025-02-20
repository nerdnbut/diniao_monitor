<template>
    <div>
      <el-form :model="localAlarm">
        <el-form-item label="报警阈值" :label-width="'120px'">
          <el-input v-model="localAlarm.threshold" placeholder="请输入阈值" />
        </el-form-item>
        <el-form-item label="报警级别" :label-width="'120px'">
          <el-select v-model="localAlarm.alarmLevel" placeholder="选择报警级别">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
  </template>
  
  <script lang="ts">
  export default {
    props: {
      selectedAlarm: {
        type: Object,
        required: true,
      },
    },
    data() {
      return {
        // 创建本地副本来修改数据
        localAlarm: { ...this.selectedAlarm },
      };
    },
    watch: {
      selectedAlarm(newVal) {
        // 如果父组件的数据改变，更新本地副本
        this.localAlarm = { ...newVal };
      },
    },
    // 暴露 localAlarm 给父组件
    expose: ['localAlarm'], // Options API 的暴露方式
  };
  </script>