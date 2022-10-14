<template>
  <span>
    <v-tabs :height="40" v-model="selected_tab" @change="handleChange">
      <v-tab>
        <v-icon class="mr-1">mdi-web</v-icon>
        {{ $t('tabs.login') }}
        <span
          v-if="stats.login"
          class="ml-1"
        >
          ({{ stats.login }})
        </span>
      </v-tab>
      <v-tab>
        <v-icon class="mr-1">mdi-server</v-icon>
        {{ $t('tabs.server') }}
        <span
          v-if="stats.server"
          class="ml-1"
        >
          ({{ stats.server }})
        </span>
      </v-tab>
      <v-tab>
        <v-icon class="mr-1">mdi-phone</v-icon>
        {{ $t('tabs.phone') }}
        <span
          v-if="stats.phone"
          class="ml-1"
        >
          ({{ stats.phone }})
        </span>
      </v-tab>
      <v-tab>
        <v-icon class="mr-1">mdi-bank</v-icon>
        {{ $t('tabs.bank') }}
        <span
          v-if="stats.bank"
          class="ml-1"
        >
          ({{ stats.bank }})
        </span>
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="selected_tab">
      <v-tab-item key="login">
        <secret ref="login" category="login"/>
      </v-tab-item>
      <v-tab-item key="server">
        <secret ref="server" category="server"/>
      </v-tab-item>
      <v-tab-item key="phone">
        <secret ref="phone" category="phone"/>
      </v-tab-item>
      <v-tab-item key="bank">
        <secret ref="bank" category="bank"/>
      </v-tab-item>
    </v-tabs-items>
  </span>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import { mapGetters } from 'vuex'
import secret from "./Secret.vue"
import http from "@/utils/http"
import EventBus from "@/event"

export default defineComponent({
  name: 'Home',
  components: {
    secret
  },
  
  data: () => ({
    selected_tab: 0,
    tabs: ["login", "server", "phone", "bank"],
    stats: {
      login: 0,
      server: 0,
      phone: 0,
      bank: 0
    }
  }),

  computed: {
    ...mapGetters({
      current_folder: 'getFolder',
    })
  }, 

  mounted(){
    EventBus.$on("selectedFolder", (folder) => {
      this.getStats(folder._id)
    })

    EventBus.$on("refreshStats", () => {
      this.getStats(this.current_folder)
    })

    EventBus.$on("showTrash", (val) => {
      if (val === true) this.getStats("",true)
    })

    EventBus.$on("refreshTrashStats", () => {
      this.getStats("",true)
    })

    EventBus.$on("refreshSecrets", () => {
      this.$refs[this.tabs[this.selected_tab]].getSecrets()
    })
  },

  methods: {
    getStats(folder, showTrash = false) {
      const url = showTrash === true ? 
        `/api/v1/workspace/${sessionStorage.getItem("current_workspace")}/trash/stats` : 
        `/api/v1/folder/${folder}/stats/`

      http.get(url).then((response) => {
        this.stats = response.data;
      })
    },

    handleChange(val) {
      setTimeout(() => {
        this.selected_tab = val
        for (const i in this.tabs) {
          if (parseInt(i) === val) {
            if (this.$refs[this.tabs[i]])
              this.$refs[this.tabs[i]].getSecrets()
          } else {
            if (this.$refs[this.tabs[i]])
              this.$refs[this.tabs[i]].keys = []
          }
        }
      }, 200);
    }
  }
})
</script>

