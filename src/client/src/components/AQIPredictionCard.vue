<script setup lang="ts">
// define props location, and predictions
import {ref, defineProps} from 'vue'
import {BarChart} from "@/components/ui/chart-bar";

const props = defineProps<{
  location: string;
  predictions: Array<{ time: string, aqi: number }>;
}>();

const xFormatter = (tick: string, i: number) => {
  const result = new Intl.DateTimeFormat('en-US').format(new Date(tick));
  console.log('xFormatter', result);
  return result;
}

const yFormatter = (tick: number, i: number) => {
  const result = new Intl.NumberFormat('de-DE').format(tick);
  console.log('yFormatter', result);
  return result;
}
</script>

<template>
  <BarChart
      :data="props.predictions"
      index="time"
      :categories="['aqi']"
      :y-formatter="yFormatter"
      :x-formatter="xFormatter"
      :type="'stacked'"
      :show-x-axis="true"
      :show-y-axis="true"
      :show-legend="true"
      :show-grid="true"
      :show-tooltip="true"
      :title="'AQI Prediction for ' + props.location"
      :colors="['#3182CE']"
  />
</template>

<style scoped>

</style>