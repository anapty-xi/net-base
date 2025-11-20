<template>
  <div class="login-page-container">
    <LoginForm />
  </div>
</template>

<script setup>
import LoginForm from '@/components/LoginForm.vue'; 
import TablesView from '@/components/TablesView.vue'; 
</script>

<style scoped>
.login-page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh; 
}
</style>