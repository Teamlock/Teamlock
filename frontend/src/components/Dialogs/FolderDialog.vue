<template>
    <v-dialog v-model="open" width="600" scrollable>
        <v-card :loading="loading">
            <v-form ref="form" @submit.prevent="saveFolder">
                <v-app-bar flat dense>
                    <v-app-bar-nav-icon v-if="form.use_icon">
                        <v-icon>{{ form.icon}}</v-icon>
                    </v-app-bar-nav-icon>
                    <v-app-bar-title class="pl-0">
                        {{ $t('label.folder') }}
                    </v-app-bar-title>
                </v-app-bar>
                <v-card-text>
                    <v-row dense>
                        <v-col>
                            <v-text-field ref="folderName" v-model="form.name" :label="$t('label.folder_name')" hide-details />
                        </v-col>
                    </v-row>
                    <v-row dense class="mt-4">
                        <v-select 
                            :items="iconsList"
                            v-model="form.icon"
                            :label="$t('label.select_icon')"
                            item-text="text"
                            item-value="icon"
                        >
                            <template slot="selection" slot-scope="data">
                                <v-icon class="mr-1">{{data.item.icon}}</v-icon> {{ data.item.text }}
                            </template>
                            <template slot="item" slot-scope="data">
                                <v-icon class="mr-1">{{data.item.icon}}</v-icon> {{ data.item.text }}
                            </template>
                        </v-select>
                    </v-row>
                      <v-row dense>
                            <v-switch 
                                v-model="form.custom_policy"
                                class="m-0"
                                :label="$t('label.password_policy')"
                                hide-details
                            />
                        </v-row>
                        <span v-if="form.custom_policy">
                            <v-row>
                                <p class="mt-5 ml-3">
                                    <small>
                                        <v-icon>mdi-information-outline</v-icon> {{ $t('help.policy_password_folder') }}
                                    </small>
                                </p>
                            </v-row>
                            <v-row dense>
                                <v-col class="text-left">
                                    <label>{{ $t('label.password_length') }}</label>
                                    <v-slider
                                        :disabled="!form.custom_policy"
                                        v-model="form.password_policy.length"
                                        max="100"
                                        min="0"
                                        track-color="#E2E2E2"
                                    >
                                        <template v-slot:append>
                                            <v-text-field
                                                v-model="form.password_policy.length"
                                                class="mt-0 pt-0"
                                                :disabled="!form.custom_policy"
                                                hide-details
                                                single-line
                                                type="number"
                                                style="width: 60px"
                                            />
                                        </template>
                                    </v-slider>
                                </v-col>
                            </v-row>
                            <v-row dense>
                                <v-col class="text-left">
                                    <label>{{ $t('label.password_upper') }}</label>
                                    <v-slider
                                        :disabled="!form.custom_policy"
                                        v-model="form.password_policy.uppercase"
                                        :max="form.password_policy.length"
                                        min="0"
                                        track-color="#E2E2E2"
                                    >
                                        <template v-slot:append>
                                            <v-text-field
                                                v-model="form.password_policy.uppercase"
                                                class="mt-0 pt-0"
                                                :disabled="!form.custom_policy"
                                                hide-details
                                                single-line
                                                type="number"
                                                style="width: 60px"
                                            />
                                        </template>
                                    </v-slider>
                                </v-col>
                            </v-row>
                            <v-row dense>
                                <v-col class="text-left">
                                    <label>{{ $t('label.password_number') }}</label>
                                    <v-slider
                                        :disabled="!form.custom_policy"
                                        v-model="form.password_policy.numbers"
                                        :max="form.password_policy.length - form.password_policy.uppercase"
                                        min="0"
                                        track-color="#E2E2E2"
                                    >
                                        <template v-slot:append>
                                            <v-text-field
                                                v-model="form.password_policy.numbers"
                                                class="mt-0 pt-0"
                                                :disabled="!form.custom_policy"
                                                hide-details
                                                single-line
                                                type="number"
                                                style="width: 60px"
                                            />
                                        </template>
                                    </v-slider>
                                </v-col>
                            </v-row>
                            <v-row dense>
                                <v-col class="text-left">
                                    <label>{{ $t('label.password_special') }}</label>
                                    <v-slider
                                        :disabled="!form.custom_policy"
                                        v-model="form.password_policy.special"
                                        :max="form.password_policy.length - (form.password_policy.uppercase + form.password_policy.numbers)"
                                        min="0"
                                        track-color="#E2E2E2"
                                    >
                                        <template v-slot:append>
                                            <v-text-field
                                                v-model="form.password_policy.special"
                                                class="mt-0 pt-0"
                                                :disabled="!form.custom_policy"
                                                hide-details
                                                single-line
                                                type="number"
                                                style="width: 60px"
                                            />
                                        </template>
                                    </v-slider>
                                </v-col>
                            </v-row>
                        </span>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn text small @click="closeDialog">{{ $t('button.cancel') }}</v-btn>
                    <v-btn color="primary" small text type="submit">{{ $t('button.submit') }}</v-btn>
                </v-card-actions>
            </v-form>
        </v-card>
    </v-dialog>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import varMixin from "@/mixins/var"
import { mapGetters } from 'vuex'
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
    mixins: [varMixin],

    data: () => ({
        folder_id: null,
        parent_id: null,
        open: false,
        loading: false,
        form: {
            name: "",
            icon: "mdi-folder",
            custom_policy: false,
            password_policy: {
                length: 12,
                uppercase: 1,
                numbers: 1,
                special: 1  
            }
        }
    }),

    computed: {
        ...mapGetters({
            selected_workspace: 'getWorkspace'
        }),
    },

    watch: {
    },

    mounted() {
        EventBus.$on("editFolder", (folder_id, parent_id) => {
            this.open = true;
            this.folder_id = folder_id
            this.parent_id = parent_id

            if (this.folder_id)
                this.fetchFolder()

            setTimeout(() => {
                this.$refs.folderName.focus()
            }, 200);
        })
    },

    methods: {
        fetchFolder() {
            this.loading = true;
            const uri = `/api/v1/folder/${this.folder_id}`

            http.get(uri).then((response) => {
                let form = response.data
                if (!form.password_policy) {
                    form.password_policy = {
                        length: 12,
                        uppercase: 1,
                        numbers: 1,
                        special: 1  
                    }
                } else {
                    form.custom_policy = true
                }

                this.form = form
            }).then(() => {
                this.loading = false
            })
        },

        async saveFolder() {
            this.loading = true
            let uri = `/api/v1/folder/`
            let message = this.$t("success.folder_created")
            let folder_id = this.folder_id

            let form = this.form
            form.workspace = this.selected_workspace._id
            form.parent = this.parent_id

            if (!form.custom_policy) {
                form.password_policy = null
            }

            if (this.folder_id) {
                uri += this.folder_id
                await http.put(uri, form)
                message = this.$t("success.folder_updated")
            } else {
                let response = await http.post(uri, form)
                folder_id = response.data
            }

            this.$toast.success(message, {
                closeOnClick: true,
                timeout: 3000,
                icon: true
            })

            this.loading = false
            this.closeDialog()

            localStorage.setItem("selected_folder", folder_id)
            EventBus.$emit("refreshTreeview")
        },

        closeDialog() {
            this.form = {
                name: "",
                icon: "mdi-folder",
                password_policy: {
                    length: 12,
                    uppercase: 1,
                    numbers: 1,
                    special: 1
                }
            }
            this.open = false
        }
    }
})
</script>
