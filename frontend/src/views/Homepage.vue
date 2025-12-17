<template>
  
  <div class="homepage-container">
    <div class="tables-container" style="margin-top: 7rem; margin-left: 2rem;">
        <TablesView />
    </div>
    <div class="account-container" style="margin-top: 12rem; margin-left: 20rem;">
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