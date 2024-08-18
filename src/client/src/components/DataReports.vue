<script setup lang="ts">
import {onMounted, Ref, ref} from "vue";
import ComboBox from "@/components/ComboBox.vue";
import {Location} from "@/models";
import L from "leaflet";

const GET_LOCATIONS_URL = 'https://backend-production-ce7e.up.railway.app/api' + '/locations';
const DATA_DRIFT_URL = 'https://backend-production-ce7e.up.railway.app/api' + '/reports/data-drift';
const DATA_STABILITY_URL = 'https://backend-production-ce7e.up.railway.app/api' + '/reports/data-stability';

const locations: Ref<Array<Location>> = ref([]);
const currentLocation = ref<string | null>(null);

const dataDriftHtmlContent = ref<string>("");
const dataStabilityHtmlContent = ref<string>("");

onMounted(async () => {

  fetch(GET_LOCATIONS_URL)
      .then(response => response.json())
      .then(data => {
        locations.value = data;
      });

});

const onLocationSelected = async (selectedLocation: Location) => {
  currentLocation.value = selectedLocation.name;

  try {
    const response = await fetch(DATA_DRIFT_URL + '/' + currentLocation.value);
    if (response.ok) {
      dataDriftHtmlContent.value = await response.text();
    } else {
      console.error('Failed to fetch HTML:', response.statusText);
    }
  } catch (error) {
    console.error('Error fetching HTML:', error);
  }

  try {
    const response = await fetch(DATA_STABILITY_URL + '/' + currentLocation.value);
    if (response.ok) {
      dataStabilityHtmlContent.value = await response.text();
    } else {
      console.error('Failed to fetch HTML:', response.statusText);
    }
  } catch (error) {
    console.error('Error fetching HTML:', error);
  }
}
</script>

<template>
  <div class="flex flex-col text-center">
    <ComboBox :locations="locations" @location-selected="onLocationSelected" class="mb-7" />

    <div v-if="currentLocation" class="mb-7">
      <h2 class="font-bold">
        Data Drift and Data Stability reports for {{ currentLocation }}
      </h2>
      <div class="html-container-drift mb-7" v-html="dataDriftHtmlContent"></div>
      <div class="html-container-stability" v-html="dataStabilityHtmlContent"></div>
    </div>

    <div v-else class="mb-7">
      <h2 class="font-bold">
        Please select a location to view reports.
      </h2>
    </div>
  </div>
</template>

<style scoped>
.html-container-drift > * {
  height: 1500px;
}
.html-container-stability > * {
  height: 6600px;
}
</style>
