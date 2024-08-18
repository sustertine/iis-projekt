<script setup lang="ts">
import {ref} from 'vue'
import {Check, ChevronsUpDown} from 'lucide-vue-next'
import {Button} from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import {cn} from "@/lib/utils.ts";
import {Location} from "@/models";


const locationSelected = defineEmits<{ (e: 'location-selected', location: Location): void }>();

const open = ref(false)
const selection = ref('')

const props = defineProps<{
  locations: Array<Location>;
}>();


const handleSelection = (event: any) => {
  selection.value = event.detail.value;
  open.value = false;
  const location = props.locations.find((location) => location.name === event.detail.value);
  locationSelected('location-selected', location);
}

</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button
          variant="outline"
          role="combobox"
          :aria-expanded="open"
          class="w-[200px] justify-between"
      >
        {{
          selection
              ? locations.find((location) => location.name === selection)?.name
              : "Select location..."
        }}
        <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-[200px] p-0">
      <Command>
        <CommandInput class="h-9" placeholder="Search location..." />
        <CommandEmpty>No locations found.</CommandEmpty>
        <CommandList>
          <CommandGroup>
            <CommandItem
                v-for="location in props.locations"
                :key="location.name"
                :value="location.name"
                @select="handleSelection($event)"
            >
              {{ location.name }}
              <Check
                  :class="cn(
                  'ml-auto h-4 w-4',
                  selection === location.name ? 'opacity-100' : 'opacity-0',
                )"
              />
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>

<style scoped>

</style>