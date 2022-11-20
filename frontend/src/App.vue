<template>
  <div id="app" @click="appClick">
    <router-view />

    <portal-target name="contextMenuFolder" />
    <portal-target name="contextMenuWorkspace" />
  </div>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import EventBus from "@/event.js"
import i18n from '@/plugins/i18n';
import { mapGetters } from 'vuex'

export default defineComponent({

  computed: {
      ...mapGetters({
          user: 'getUser'
      })
  },

  beforeMount() {
    EventBus.$emit("showTrash", false);
    let lang = localStorage.getItem("lang")
    if (lang) {
      i18n.locale = lang
      this.$vuetify.lang.current = lang
    }

    this.$store.dispatch("set_pro")
    if (sessionStorage.getItem("token")) {
      this.$store.dispatch("set_user")
      this.$store.dispatch("set_twilio")
    }

    if (localStorage.getItem("teamlock_theme") === "light") {
      this.$vuetify.theme.dark = false
    } else {
      this.$vuetify.theme.dark = true
    }
  },

  mounted() {
    setTimeout(() => {
      if (this.user) {
        if (!this.user.recovery_key_downloaded) {
          this.$toast.warning(this.$t("warning.reminder_download_recovery2"), {
              position: "top-center",
              timeout: 10000
          })
        }
      }
    }, 500);
  }, 

  methods: {
    appClick() {
      EventBus.$emit("closeContext")
    }
  }
})
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
