<template>
  
  <div class="homepage-container">
    <div class="tables-container">
        <TablesView />
    </div>
    <div class="account-container">
        <Account />
    </div>
    
  </div>
</template>

<script setup>
import Account from '@/components/Account.vue'; 
import TablesView from '@/components/TablesView.vue'; 
</script>

<style scoped>
.homepage-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  min-height: 80vh; 
}
</style>