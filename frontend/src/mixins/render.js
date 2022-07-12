import moment from "moment"

const renderMixin = {
    methods: {
        renderCountry(country) {
            return require(`@/assets/img/flags/${country.toLowerCase()}.svg`)
        },

        renderClassBG() {
            const classe = this.$vuetify.theme.dark ? "bg-dark" : "bg-white"
            return classe
        },

        renderAppStyle() {
            const theme = this.$vuetify.theme.dark ? "dark" : "light"
            return {
                background: this.$vuetify.theme.themes[theme].background
            }
        },

        renderDate(date, format) {
            if (!format) {
                format = "DD/MM/YYYY HH:mm:ss"
            }

            const m = moment.utc(date).local().format(format)
            if (m === "Invalid date") { return this.$t("label.never") }
            return m
        },

        renderOS(os) {
            switch (os.toLowerCase()) {
                case "macos":
                    return "mdi-apple"
                case "windows":
                    return "mdi-microsoft-windows"
                case "linux":
                    return "mdi-linux"
                case "android":
                    return "mdi-android"
                case "ios":
                    return "mdi-apple-ios"
            }
        }
    }
}

export default renderMixin
