<template>
  <v-form @submit.prevent="saveRecoveryConfig">
    <v-card flat>
      <v-card-text class="text-left pt-0">
        <v-row class="">
          <v-col :md="8">
            <v-switch
              v-model="form.enabled"
              :label="$t('label.send_recovery_enabled')"
              :hint="$t('help.send_recovery_enabled')"
              persistent-hint
              class="mb-5"
            />

            <span v-if="form.enabled">
              <v-select
                :label="$t('label.product_type')"
                v-model="form.config.product_type"
                :items="available_product"
                item-text="text"
                item-value="value"
              />

              <s-3 v-if="form.config.product_type === 's3'" v-model="form.config" />
              <sftp v-if="form.config.product_type === 'sftp'" v-model="form.config" />
            </span>
          </v-col>

          <v-col :md="4" v-if="form.enabled">
            <v-card
              :loading="is_loading_test"
              class="mt-5"
              outlined
              raised
              tile
              hover
            >
              <v-card-text class="">
                <p class="text-h5 text--primary">
                  {{ $t('title.test_configuration' )}}
                </p>

                <v-btn
                  @click="testRecovery()"
                  :loading="is_loading_test"
                  elevation-10
                  color="primary"
                  small
                >
                  <v-icon>mdi-flash</v-icon>
                  {{ $t('button.test') }}
                </v-btn>

                <p v-if="form_valid" class="mt-5 mb-0">
                  <v-alert
                    type="success"
                    icon="mdi-check"
                    class="mb-0"
                  >
                    {{ $t('success.recovery_ok') }}
                  </v-alert>

                  <br/>

                  <json-viewer
                    style="max-height: 400px; overflow: auto"
                    :value="test_result"
                    theme="jv-dark"
                    copyable
                  />
                </p>
                <p v-if="error" class="mt-5 mb-0">
                  <v-alert
                    type="error"
                    icon="mdi-close-box"
                    class="mb-0"
                  >
                    {{ error }}
                  </v-alert>
                </p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions v-if="form_valid || !form.enabled">
        <v-spacer></v-spacer>
        <v-btn color="primary" :loading="is_loading" type="submit">{{ $t('button.save') }}</v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </v-card>
  </v-form>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import JsonViewer from 'vue-json-viewer'
import http from "@/utils/http"
import sftp from './sftp.vue'
import s3 from './s3.vue'

export default defineComponent({
  components: {
    JsonViewer,
    sftp,
    s3
  },
  data: () => ({
    form: {
      enabled: false,
      config: {}
    },
    form_valid: false,
    test_result: "",
    error: "",
    is_loading: false,
    is_loading_test: false,
    available_product: [
      {text: 'S3', value: 's3'},
      {text: 'SFTP', value: 'sftp'}
    ]
  }),

  mounted() {
    this.getConfig()
  },

  methods: {
    async getConfig() {
      const response = await http.get("/pro/api/v1/config/recovery")
      if (response.data.config.product_type) {
        this.form = response.data
      }
    },

    saveRecoveryConfig() {
      this.is_loading = true
      if (!this.form.enabled) {
        this.form.config.product_type = "None"
      }

      http.post("/pro/api/v1/config/recovery", this.form)
      .then(() => {
        this.$toast.success(this.$t("success.recovery_save"))
      }).catch(() => {
        this.$toast.error(this.$t("error.occurred"))
      }).then(() => {
        this.is_loading = false
      })
    },

    testRecovery() {
      this.is_loading_test = true
      this.test_result = ""
      this.form_valid = false
      this.error = ""

      http.post(
        "/pro/api/v1/config/recovery/test",
        this.form
      ).then(({ data }) => {
        this.test_result = data
        this.form_valid = true
      }).catch((err) => {
        if (err.response.status === 422) {
          this.error = this.$t("error.invalid_form")
        } else {
          this.error = err.response.data.detail
        }
      }).then(() => {
        this.is_loading_test = false
      })
    }
  }
})
</script>
<style scoped>
</style>