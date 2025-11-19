<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <header class="app-header">
      <nav>
        <router-link to="/login">Вход</router-link> 
        </nav>
    </header>

    <main class="app-content">
      <router-view />
    </main>

    <footer class="app-footer">
      <p>&copy; anapty-xi</p>
    </footer>
  </div>
</template>



