<script setup lang="ts">
// define props location, and predictions
import {defineProps} from 'vue'
import {BarChart} from "@/components/ui/chart-bar";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card";

const props = defineProps<{
  location: string;
  predictions: Array<{ time: string, aqi: number }>;
}>();

const xFormatter = (tick: string, i: number) => {
  return new Intl.DateTimeFormat('de-DE').format(new Date(tick));
}

const yFormatter = (tick: number, i: number) => {
  return new Intl.NumberFormat('de-DE').format(tick);
}

const getTodaysDate = () => {
  const today = new Date();
  const dd = String(today.getDate()).padStart(2, '0');
  const mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
  const yyyy = today.getFullYear();

  return dd + '.' + mm + '.' + yyyy;
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>
        {{ props.location }} - {{ getTodaysDate() }}
      </CardTitle>
      <CardDescription>
        European AQI Prediction for the next 24 hours
      </CardDescription>
    </CardHeader>
    <CardContent>
      <BarChart
          :data="props.predictions"
          index="time"
          :categories="['aqi']"
          :type="'stacked'"
          :y-formatter="yFormatter"
          :x-formatter="xFormatter"
          :show-x-axis="true"
          :show-y-axis="true"
          :show-legend="true"
          :show-grid="true"
          :show-tooltip="true"
          :title="'AQI Prediction for ' + props.location"
          :colors="['#3182CE']"
      />
    </CardContent>
  </Card>

</template>

<style scoped>

</style>