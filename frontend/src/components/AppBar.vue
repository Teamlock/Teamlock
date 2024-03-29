<template>
    <v-app-bar
        app
        height="58"
        class="bg_appbar"
    >
        <span v-if="currentRouteName === 'Admin'" class="text_label_app_bar">
            <v-icon>mdi-cogs</v-icon>&nbsp;
            {{ $t('label.admin') }}
        </span>
        <span v-else-if="currentRouteName === 'Users'"  class="text_label_app_bar">
            <v-icon>mdi-account-group</v-icon>&nbsp;
            {{ $t('label.users') }}
        </span>
        <span v-else-if="currentRouteName === 'Profile'" class="text_label_app_bar">
            <v-icon>mdi-account-box</v-icon>&nbsp;
            {{ $t('label.profile') }}
        </span>
        <span v-else-if="currentRouteName === 'Sessions'" class="text_label_app_bar">
            <v-icon>mdi-account-clock</v-icon>&nbsp;
            {{ $t('label.sessions') }}
        </span>
        <span v-else-if="currentRouteName === 'History'" class="text_label_app_bar">
            <v-icon>mdi-clock</v-icon>&nbsp;
            {{ $t('label.history') }}
        </span>
        <span v-else-if="showTrash" class="text_label_app_bar">
            <v-icon>mdi-delete</v-icon>&nbsp;
            {{ $t('label.trash') }}
        </span>
        <span v-else-if="selectedFolder" class="text_label_app_bar">
            <v-icon>{{selectedFolder.icon}}</v-icon>
            {{ selectedFolder.name|str_limit(40) }}

            <v-tooltip
                v-model="tooltip_copy"
                bottom
            >
                <template v-slot:activator="{ on, attrs }">
                <v-btn
                    v-bind="attrs"
                    v-on="on"
                    @click.stop="copyFolderID(selectedFolder._id)"
                    small
                    icon
                    tile
                >
                    <v-icon small>mdi-content-copy</v-icon>
                </v-btn>
                </template>
                <span v-html="tooltipFolderId" />
            </v-tooltip>
        </span>
        <v-spacer></v-spacer>
        
        <small id="version">
            v{{version}}
        </small>

         <v-text-field
            v-if="searchBar"
            flat
            dense
            clearable
            hide-details
            class="mr-2"
            solo-inverted
            v-model="search"
            ref="globalSearch"
            @keyup.enter="searchKeys"
            :placeholder="$t('label.search_bar')"
        >
            <v-icon slot="prepend">
                mdi-search
            </v-icon>
        </v-text-field>

        <v-switch v-model="$vuetify.theme.dark" @change="setTheme" small @click.stop class="mr-2 mt-5">
            <template v-slot:label>
                <v-icon v-html="iconDarkMode" />
            </template>
        </v-switch>

        <v-menu offset-y>
            <template v-slot:activator="{ on, attrs }">
                <v-btn
                    text
                    v-bind="attrs"
                    v-on="on"
                    class=""
                >
                    <v-img :src="flags[$vuetify.lang.current]" width="20" />
                </v-btn>
            </template>
            <v-list>
                <v-list-item
                    v-for="(item, index) in langs"
                    :key="index"
                >
                    <v-btn text small block @click="changeLang(item)">
                        <v-img :src="flags[item]" width="30"/>
                    </v-btn>
                </v-list-item>
            </v-list>
        </v-menu>

        <span v-if="isPro">
            <notification/>
        </span>

        <v-menu
            v-if="user"
            left
            bottom
            offset-y
        >
            <template v-slot:activator="{ on, attrs }">
                <v-btn
                    icon
                    x-small
                    v-bind="attrs"
                    v-on="on"
                    class="mr-0 ml-2"
                >
                    <!-- <v-img :src="image" max-width="45" ></v-img> -->
                    <v-icon color="primary" large>mdi-account-box</v-icon>
                </v-btn>
            </template>

            <v-list class="no-padding">
                <span v-if="user.is_admin">
                    <v-list-item to="/admin">
                        <v-list-item-title><v-icon>mdi-cogs</v-icon>&nbsp;{{ $t('label.admin') }}</v-list-item-title>
                    </v-list-item>
                    <v-divider />
                </span>
                <v-list-item to="/profile">
                    <v-list-item-title><v-icon>mdi-account</v-icon>&nbsp;{{ $t('label.profile') }}</v-list-item-title>
                </v-list-item>
                <v-list-item @click="logout">
                    <v-list-item-title><v-icon>mdi-logout</v-icon>&nbsp;{{ $t('label.logout') }}</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
    </v-app-bar>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import Notification from './Notification.vue';
import { mapGetters } from 'vuex'
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
    components: {Notification},

    props: {
        searchBar: {
            type: Boolean,
            default: false
        }
    },

    computed: {
        ...mapGetters({
            user: 'getUser',
            isPro: 'getPro'
        }),
        currentRouteName() {
            return this.$route.name;
        },
        iconDarkMode() {
            if (this.$vuetify.theme.dark) {
                return "mdi-weather-night"
            } else {
                return "mdi-white-balance-sunny"
            }
        },
    },

    data: (vm) => ({
        search: "",
        tooltip_copy: false,
        tooltipFolderId: vm.$t('tooltip.copy_id'),
        mapping_flags: {
            "en": "gb",
            "fr": "fr"
        },
        version : null,
        langs: ["en", "fr"],
        selectedFolder: null,
        showTrash: false,
        image: require("@/assets/img/man.svg"),
        flags: {
            en: require("@/assets/img/flags/en.svg"),
            fr: require("@/assets/img/flags/fr.svg"),
        }
    }),

    beforeMount() {
        const userAgent = navigator.userAgent.toLowerCase();
        this.electron = userAgent.indexOf(' electron/') > -1
    },

    mounted() {
        window.addEventListener("keydown", (e) => {
            if (e.ctrlKey && e.key === ":") {
                this.$refs.globalSearch.focus()
            }
        })

        EventBus.$on("selectedFolder", (folder) => {
            this.selectedFolder = folder
        })

        EventBus.$on("showTrash",(val) => this.showTrash = val)
        this.showTrash = localStorage.getItem("showTrash") === "true"
        this.getVersion()
    },

    methods: {
        changeLang(lang) {
            localStorage.setItem("lang", lang)
            window.location.reload()
        },
        
        searchKeys() {
            if (this.search === "") {
                this.getSecrets()
            } else {
                EventBus.$emit("searchSecrets", this.search)
            }
        },

        getSecrets() {
            EventBus.$emit("refreshSecrets")
        },

        logout() {
            EventBus.$emit("stopKeepAlive")
            sessionStorage.clear()

            if (!this.electron) {
                this.$router.push("/login")
            } else {
                window.ipc.send("LOGOUT")
            }
        },

        setTheme() {
            const theme = this.$vuetify.theme.dark ? "dark": "light"
            localStorage.setItem("teamlock_theme", theme)
        },

        copyFolderID(folder_id) {
            this.$copyText(folder_id)

            setTimeout(() => {
                this.tooltipFolderId = this.$t("help.copied")
                this.tooltip_copy = true

                setTimeout(() => {
                    this.tooltip_copy = false

                    setTimeout(() => {
                        this.tooltipFolderId = this.$t("tooltip.copy_id")
                    }, 500);
                }, 1000);
            }, 50);
        },
        getVersion(){
            http.get("/api/v1/version")
                .then(response => {
                    this.version = response.data
                })
        }
    }
})
</script>