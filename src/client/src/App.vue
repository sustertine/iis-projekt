<script setup lang="ts">
import NavMenu from "@/components/NavMenu.vue";
import { Separator } from '@/components/ui/separator'
import ThemeSwitch from "@/components/ThemeSwitch.vue";
</script>

<template>
  <div class="flex h-screen py-1 px-16">
    <main class="flex-grow p-4">
      <div class="flex justify-center mb-2 p-2">
        <NavMenu/>
      </div>
      <Separator label="AQ Monitor" />
      <div class="flex-grow w-full py-4">
        <router-view/>
      </div>
    </main>
  </div>
</template>

<style scoped>
</style>
