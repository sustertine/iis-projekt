<script setup lang="ts">

import {onMounted, ref, Ref} from "vue";
import {Location, ModelMetadata} from "@/models";
import ComboBox from "@/components/ComboBox.vue";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import {Separator} from "@/components/ui/separator";
import {BarChart} from "@/components/ui/chart-bar";
import {AreaChart} from "@/components/ui/chart-area";

const GET_LOCATIONS_URL = import.meta.env.VITE_SERVER_URL + '/locations';
const GET_METRICS_URL = import.meta.env.VITE_SERVER_URL + '/reports/model-metrics';
const GET_METADATA_URL = import.meta.env.VITE_SERVER_URL + '/reports/model-metadata';
const GET_LATEST_PREDICTIONS_URL = import.meta.env.VITE_SERVER_URL + '/reports/latest-predictions';

const locations: Ref<Array<Location>> = ref([]);
const currentLocation = ref<string | null>(null);

const metrics = ref<any>(null);
const metadata = ref<ModelMetadata | null>(null);
const latestPredictions = ref<any>(null);

onMounted(async () => {
  fetch(GET_LOCATIONS_URL)
      .then(response => response.json())
      .then(data => {
        locations.value = data;
      });
});

const onLocationSelected = async (selectedLocation: Location) => {
  currentLocation.value = selectedLocation.name;
  fetch(GET_METRICS_URL + '/' + selectedLocation.name)
      .then(response => response.json())
      .then(data => {
        metrics.value = data;
      });

  fetch(GET_METADATA_URL + '/' + selectedLocation.name)
      .then(response => response.json())
      .then(data => {
        metadata.value = data;
      });

  fetch(GET_LATEST_PREDICTIONS_URL + '/' + selectedLocation.name)
      .then(response => response.json())
      .then(data => {
        latestPredictions.value = data;
      });
}

const roundValue = (value: number) => {
  return value.toFixed(3);
}

const normalizeKey = (key: string) => {
  const replacedKey = key.replace(/_/g, ' ');

  if (replacedKey.includes(' ')) {
    return replacedKey.replace(/\b\w/g, (char: string) => char.toUpperCase());
  } else {
    return replacedKey.toUpperCase();
  }
}

const formatDate = (timestamp: number) => {
  const date = new Date(timestamp);
  return date.toLocaleString('de-DE');
}

const calculateDuration = (start: number, end: number) => {
  const durationMs = end - start;
  const durationMin = Math.floor(durationMs / 60000);
  const durationSec = ((durationMs % 60000) / 1000).toFixed(0);
  return `${durationMin}m ${durationSec}s`;
}

const parseParams = () => {
  return metadata.value.params;
}

const reduceAndSortPredictions = () => {
  const allPredictions = latestPredictions.value.flatMap((data: Record<string, any>) => data.evaluated_predictions);
  return allPredictions;
}
</script>

<template>
  <div class="flex flex-col text-center">
    <ComboBox :locations="locations" @location-selected="onLocationSelected" class="mb-7"/>

    <div v-if="currentLocation" class="mb-7">
      <h2 class="font-bold mb-3">
        Production model: {{ currentLocation }}
      </h2>
      <Card v-if="metadata">
        <CardHeader>
          <CardTitle>Model Metadata</CardTitle>
        </CardHeader>
        <CardContent>
          <p><span class="font-bold">Model Name:</span> {{ metadata?.model_name }}</p>
          <p><span class="font-bold">Run ID:</span> {{ metadata?.run_id }}</p>
          <p><span class="font-bold">Start Time:</span> {{ formatDate(metadata?.start_time) }}</p>
          <p><span class="font-bold">End Time:</span> {{ formatDate(metadata?.end_time) }}</p>
          <p><span class="font-bold">Build Duration:</span>
            {{ calculateDuration(metadata?.start_time, metadata?.end_time) }}</p>
          <p><span class="font-bold">Status:</span> {{ metadata?.status }}</p>
        </CardContent>
      </Card>
      <Separator label="Metrics" class="my-3"/>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <Card v-for="(value, key) in metrics" :key="key">
          <CardHeader>
            <CardTitle>
              {{ roundValue(value) }}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {{ normalizeKey(key.toString()) }}
          </CardContent>
        </Card>
      </div>
      <Separator label="Parameters" class="my-3"/>
      <Table v-if="metadata">
        <TableHeader>
          <TableRow>
            <TableHead>Parameter</TableHead>
            <TableHead>Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="(value, key) in parseParams()" :key="key" class="font-medium">
            <TableCell class="text-start">{{ normalizeKey(key.toString()) }}</TableCell>
            <TableCell class="text-start">{{ value }}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
      <Separator label="Predictions from production" class="my-3"/>
      <h1>
        AQI Predictions
      </h1>
      <AreaChart v-if="latestPredictions"
                 :data="reduceAndSortPredictions()"
                 index="time"
                 :categories="['aqi', 'actual_aqi', 'mae', 'mse', 'rmse']"
                 :colors="['#3182CE', '#00ff20', '#f3ff7e', '#f33c3c', '#FFA500']"/>
    </div>
    <div v-else class="mb-7">
      <h2 class="font-bold">
        Please select a model
      </h2>
    </div>
  </div>
</template>

<style scoped>

</style>