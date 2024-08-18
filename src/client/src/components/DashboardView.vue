<script setup lang="ts">

import DataReports from "@/components/DataReports.vue";
import {Tabs, TabsList, TabsTrigger, TabsContent} from "@/components/ui/tabs";
import ModelDetailsView from "@/components/ModelDetailsView.vue";
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
      <ModelDetailsView/>
    </TabsContent>
    <TabsContent value="data">
      <DataReports/>
    </TabsContent>
  </Tabs>
</template>

<style scoped>

</style>