<template>
  <span>
    <v-tabs :height="40" v-model="selected_tab">
      <v-tab>{{ $t('label.secrets') }}</v-tab>
      <!-- <v-tab>Files</v-tab> -->
    </v-tabs>
    <v-tabs-items v-model="selected_tab">
      <v-tab-item key="secrets">
        <secrets />
      </v-tab-item>
      <!-- <v-tab-item key="files">
        files
      </v-tab-item> -->
    </v-tabs-items>
  </span>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import Secrets from "./Secrets.vue"
import EventBus from "@/event"

export default defineComponent({
  name: 'Home',
  components: {
    Secrets
  },
  
  data: () => ({
    selected_tab: "secrets",
    is_trash:false
  }),

  mounted(){
    EventBus.$on("folder_trash",res => this.is_trash = res.is_trash);
  }
})
</script>

