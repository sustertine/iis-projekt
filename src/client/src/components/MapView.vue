<script setup lang="ts">
import {onMounted, Ref, ref} from "vue";
import ComboBox from "@/components/ComboBox.vue";
import {Location} from "@/models";
import L from 'leaflet';
import AQIPredictionCard from "@/components/AQIPredictionCard.vue";
import {Card, CardContent} from "@/components/ui/card";

const GET_LOCATIONS_URL = import.meta.env.VITE_SERVER_URL + '/locations';
const GET_PREDICTION_URL = import.meta.env.VITE_SERVER_URL + '/predict-aqi';

const locations: Ref<Array<Location>> = ref([]);
const map = ref();
const mapContainer = ref();
const currentLocation = ref<string | null>(null);
const predictions = ref<Array<{ time: string, aqi: number }> | null>(null);

onMounted(() => {
  map.value = L.map(mapContainer.value).setView([46.1204, 14.8156], 9);

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map.value);

  fetch(GET_LOCATIONS_URL)
      .then(response => response.json())
      .then(data => {
        locations.value = data;

        locations.value.forEach(location => {
          L.marker([location.lat, location.lon]).addTo(map.value);
        });
      });

});

const onLocationSelected = (selectedLocation: Location) => {
  currentLocation.value = selectedLocation.name;
  map.value.setView([selectedLocation.lat, selectedLocation.lon], 13);
  fetch(GET_PREDICTION_URL + '/' + selectedLocation.name)
      .then(response => response.json())
      .then(data => {
        predictions.value = data;
      });
}
</script>

<template>
  <div class="flex space-x-3">
    <div class="flex flex-col space-y-3">
      <ComboBox :locations="locations" @location-selected="onLocationSelected"/>
      <AQIPredictionCard :location="currentLocation" :predictions="predictions" v-if="predictions && currentLocation"/>
    </div>
      <div ref="mapContainer" style="width: 100%; height: 45rem"></div>
  </div>
</template>

<style scoped>
</style>