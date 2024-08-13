<script setup lang="ts">
import NavMenu from "@/components/NavMenu.vue";
</script>

<template>
  <div class="flex h-screen">
    <main class="flex-1 p-4">
      <div class="flex justify-center border-2 mb-2 rounded-md border-blue-500 p-2">
        <NavMenu />
      </div>
      <div class="flex-1 border-2 rounded-md border-blue-500 p-2">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
</style>
