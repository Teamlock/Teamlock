import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';

Vue.use(Vuetify);

export default new Vuetify({
    theme: {
        dark: true,
        themes: {
            dark: {
                primary: "#DAAB39",
                secondary: "#DAAB39",
                accent: "#DAAB39",
                warning: "#DAAB39",
                error: "#D32F2F",
                background: "#1E1E1E"
            },
            light: {
                primary: "#DAAB39",
                secondary: "#DAAB39",
                accent: "#DAAB39",
                warning: "#DAAB39",
                error: "#D32F2F"
            }
        }
    }
});
