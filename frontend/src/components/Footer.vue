<template>
  <footer class="main-footer">
    <p>&copy; Anapty-xi</p>
  </footer>
</template>

<script>
export default {
  name: 'TheFooter'
}
</script>

<style scoped>
.main-footer {
  background-color: var(--primary);
  color: white;
  padding: 1em;
  text-align: center;
  font-size: 0.9em;
  position: fixed;
  bottom: 0;
  width: 100%;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}
</style>