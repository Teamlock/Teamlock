<template>
  <span>
    <v-tabs :height="40" v-model="selected_tab">
      <v-tab>{{ $t('label.keys') }}</v-tab>
      <!-- <v-tab>Files</v-tab> -->
    </v-tabs>
    <v-tabs-items v-model="selected_tab">
      <v-tab-item key="keys">
        <keys />
      </v-tab-item>
      <!-- <v-tab-item key="files">
        files
      </v-tab-item> -->
    </v-tabs-items>
  </span>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import Keys from "./Keys.vue"
import EventBus from "@/event"

export default defineComponent({
  name: 'Home',
  components: {
    Keys
  },
  
  data: () => ({
    selected_tab: "keys",
    is_trash:false
  }),

  mounted(){
    EventBus.$on("folder_trash",res => this.is_trash = res.is_trash);
  }
})
</script>

