<template>
    <v-card :loading="isLoading">
        <v-form ref="form" @submit.prevent="saveShare">
            <v-card-title>
                {{ $t("title.add_user_to_workspace") }}
            </v-card-title>

            <v-card-text>
                <v-row>
                    <v-col cols="12">
                        <v-autocomplete
                            v-model="form.selectedUsers"
                            :items="availableUsers"
                            filled
                            hide-selected
                            hide-details
                            :label="$t('label.choose_users')"
                            style="width: 100%"
                            class="autocomplete-user-share"
                            item-text="email"
                            item-value="_id"
                            multiple
                        >
                            <template v-slot:selection="data">
                                <v-chip
                                    v-bind="data.attrs"
                                    :input-value="data.selected"
                                    close
                                    small
                                    dense
                                    @click:close="remove(data.item)"
                                >
                                    {{ data.item.email }}
                                </v-chip>
                            </template>
                        </v-autocomplete>
                    </v-col>
                </v-row>

                <v-row class="mb-2">
                    <v-col
                        cols="12"
                        md="3"
                        class="pt-0"
                    >
                        <v-switch
                            v-model="expire"
                            class="m-0"
                            :label="$t('label.expire')"
                            hide-details
                        />
                    </v-col>
                    <v-col md="9" class="pt-0">
                        <v-menu
                            ref="menu"
                            v-if="expire"
                            v-model="menuDatePicker"
                            :close-on-content-click="false"
                            :return-value.sync="form.expire_at"
                            transition="scale-transition"
                            offset-y
                            min-width="auto"
                        >
                            <template v-slot:activator="{ on, attrs }">
                                <v-text-field
                                    :value="localeDate(form.expire_at)"
                                    :label="$t('label.expire_at')"
                                    prepend-icon="mdi-calendar"
                                    readonly
                                    v-bind="attrs"
                                    v-on="on"
                                ></v-text-field>
                            </template>
                            <v-date-picker
                                v-model="date"
                                no-title
                                scrollable
                            >
                                <v-spacer></v-spacer>
                                <v-btn
                                    text
                                    @click="menuDatePicker = false"
                                >
                                    {{ $t('button.cancel' )}}
                                </v-btn>
                                <v-btn
                                    text
                                    color="primary"
                                    @click="$refs.menu.save(date)"
                                >
                                    {{ $t('button.ok') }}
                                </v-btn>
                            </v-date-picker>
                        </v-menu>
                    </v-col>
                </v-row>
            
                <h3 class="text-left">{{ $t("label.rights") }} :</h3>

                <v-row no-gutters>
                    <v-col>
                        <v-switch
                            :label="$t('label.can_read')"
                            color="#DAAB39"
                            readonly
                            v-model="form.can_read"
                            prepend-icon="mdi-eye"
                            :hint="$t('help.can_read')"
                            persistent-hint
                        ></v-switch>
                    </v-col>
                        
                    <v-col>
                        <v-switch
                            :label="$t('label.can_write')"
                            color="#DAAB39"
                            v-model="form.can_write"
                            prepend-icon="mdi-pencil"
                            :hint="$t('help.can_write')"
                            persistent-hint
                        ></v-switch>                    
                    </v-col>
                    <v-col>
                        <v-switch
                            :label="$t('label.can_share')"
                            color="#DAAB39"
                            v-model="form.can_share"
                            prepend-icon="mdi-share"
                            :hint="$t('help.can_share')"
                            persistent-hint
                        />
                    </v-col>
                </v-row>
                <v-row no-gutters>
                    <!-- <v-col>
                        <v-switch
                            :label="$t('label.can_export')"
                            color="#DAAB39"
                            v-model="form.can_export"
                            prepend-icon="mdi-export"
                            :hint="$t('help.can_export')"
                            persistent-hint
                        />
                    </v-col> -->
                    <v-col v-if="is_pro">
                        <v-switch
                            :label="$t('label.can_share_external')"
                            color="#DAAB39"
                            v-model="form.can_share_external"
                            prepend-icon="mdi-share-variant"
                            :hint="$t('help.can_share_external')"
                            persistent-hint
                        />
                    </v-col>
                </v-row>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn small text @click="emptyForm(); $emit('close')">{{ $t("button.cancel") }}</v-btn>
                <v-btn small color="primary" text type="submit" :loading="isLoading">{{ $t("button.submit") }}</v-btn>
            </v-card-actions>
        </v-form>
    </v-card>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import moment from "moment"
import http from "@/utils/http"

export default defineComponent({
    props: {
        selectedWorkspace: {
            type: String,
            required: true
        }
    },

    data: () => ({
        is_pro: false,
        isLoading: false,
        menuDatePicker: null,
        date: null,
        expire: false,
        form: {
            selectedUsers: [],
            expire_at: null,
            can_write: false,
            can_share: false,
            can_export: false,
            can_share_external: false,
            can_read: true,
        },
        availableUsers: []
    }),

    beforeMount() {
        this.is_pro = this.$store.state.pro
    },

    methods: {
        localeDate(date) {
            date = moment(date).format("L")
            if (date !== "Invalid date") {
                return date
            }
        },

        getUsers() {
            this.isLoading = true
            const params = {
                params: {
                    workspace_id: this.selectedWorkspace
                }
            }

            http.get("/api/v1/user/configured", params).then((response) => {
                this.availableUsers = response.data
            }).then(() => {
                this.isLoading = false
            })
        },
        remove (item) {
            for (const i in this.form.selectedUsers) {
                if (this.form.selectedUsers[i] === item._id){
                    this.form.selectedUsers.splice(i, 1)
                    break
                }
            }
        },

        emptyForm() {
            this.form.selectedUsers = []
            this.can_write = false
            this.can_share = false
            this.can_export = false
            this.can_share_external = false
            this.expire_at = null
            this.expire = false
        },

        saveShare() {
            this.isLoading = true
            const form = {
                users: this.form.selectedUsers,
                can_write: this.form.can_write,
                can_share: this.form.can_share,
                can_export: this.form.can_export,
                can_share_external: this.form.can_share_external
            }

            if (this.expire) {
                form.expire_at = this.form.expire_at
            }

            const uri = `/api/v1/workspace/${this.selectedWorkspace}/share`
            http.post(uri, form).then(() => {
                this.isLoading = false
                this.emptyForm()
                this.getUsers()

                this.$emit("reload")
                this.$emit("close")

                this.$toast.success(this.$t("success.users_added_to_workspace"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
            })
        }
    }
})
</script>
