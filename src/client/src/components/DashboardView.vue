<script setup lang="ts">

import DataReports from "@/components/DataReports.vue";
import {Tabs, TabsList, TabsTrigger, TabsContent} from "@/components/ui/tabs";
</script>

<template>
  <Tabs default-value="models">
    <TabsList>
      <TabsTrigger value="models">
        Models
      </TabsTrigger>
      <TabsTrigger value="data">
        Data
      </TabsTrigger>
    </TabsList>
    <TabsContent value="models">
      <h1>Models view</h1>
    </TabsContent>
    <TabsContent value="data">
      <DataReports></DataReports>
    </TabsContent>
  </Tabs>
</template>

<style scoped>

</style>