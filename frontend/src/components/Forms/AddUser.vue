<template>
  <v-card>
    <v-form ref="form" @submit.prevent="saveUser">
      <v-app-bar flat dense class="edit_workspace_bar">
        <v-app-bar-nav-icon>
          <v-icon>mdi-account-plus-outline</v-icon>
        </v-app-bar-nav-icon>
        <v-toolbar-title class="pl-0">
          {{ $t("title.user") }}
        </v-toolbar-title>
      </v-app-bar>

      <v-card-text>
        <v-row dense>
          <v-text-field
            v-model="form.email"
            :disabled="is_loading"
            color="#DAAB39"
            class="input-field"
            :label="$t('label.email')"
            required
          />
        </v-row>
        <v-row dense>
          <v-switch :disabled="is_loading" v-model="form.is_admin" :label="$t('label.is_admin')"/>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn
          text
          x-small
          @click="$emit('close')"
        >
          {{ $t("button.cancel") }}
        </v-btn>
        <v-btn
          color="primary"
          type="submit"
          x-small
          text
          :loading="is_loading"
        >
          {{ $t("button.save") }}
        </v-btn>
      </v-card-actions>
    </v-form>
  </v-card>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import http from "@/utils/http";

export default defineComponent({
  data: () => ({
    is_loading: false,
    form: {
      email: "",
      is_admin: false
    }
  }),

  methods: {
    saveUser() {
      this.is_loading = true
      http.post("/api/v1/user", this.form).then(() => {
        this.form.email = ""
        this.form.is_admin = false
        this.$toast.success(this.$t("success.user_created"), {
          closeOnClick: true,
          timeout: 3000,
          icon: true
        })

        this.$emit("reload")
      }).catch((error) => {
        if (error.response.status === 409) {
          this.$toast.error(this.$t("error.unique_user"), {
              closeOnClick: true,
              timeout: 3000,
              icon: true
          })
        } else {
          if (error.response.data.detail === "MAX USERS LIMIT") {
            this.$toast.error(this.$t("error.max_users_limit"), {
                closeOnClick: true,
                timeout: 5000,
                icon: true
            })
          } else {
            this.$toast.error(this.$t("error.unknown"), {
                closeOnClick: true,
                timeout: 3000,
                icon: true
            })
          }
        }
      }).then(() => {
        this.is_loading = false
      })
    }
  }
})
</script>
