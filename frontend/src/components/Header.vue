<template>
  <header class="main-header">
    <nav>
      <h1>net-base</h1>
      </nav>
  </header>
</template>

<script>
export default {
  name: 'TheHeader'
}
</script>

<style scoped>
.main-header {
  background-color: var(--primary);
  color: white;
  padding: 1em 1.5em;
  height: 4.5rem;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

nav h1 {
  margin: 0;
  font-size: 1.6em;
  font-weight: 600;
}
</style>