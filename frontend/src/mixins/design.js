const designMixin = {
  data: () => ({
    logoDark: require("@/assets/img/TLAppLogo_Baseline.svg"),
    logoWhite: require("@/assets/img/TLAppLogo_White.svg")
  }),

  computed: {
    logo() {
      return this.$vuetify.theme.dark ? this.logoWhite : this.logoDark
    },

    logoClass() {
      let classe = "mx-auto px-10 border-bottom-primary"
      if (this.$vuetify.theme.dark) {
        classe += " logoDark"
      } else {
        classe += " logo"
      }

      return classe
    }
  }
}

export default designMixin