<template>
  <v-container fluid class="no-padding full-height">
    <v-card flat class="full-height">
      <v-tabs
        v-model="tab"
        background-color="primary"
        height="40"
        dark
      >
        <v-tab key="tab-configuration">
          {{ $t("label.configuration") }}
        </v-tab>
        <v-tab key="tab-registration">
          {{ $t("label.registration") }}
        </v-tab>
        <v-tab v-if="is_pro" key="tab-pro">
          {{ $t("label.mfa") }}
        </v-tab>
        <v-tab v-if="is_pro" key="tab-recovery">
          {{ $t("label.recovery_configuration") }}
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item key="tab-configuration">
          <v-form ref="form-configuration" @submit.prevent="saveConfig">
            <v-card flat>
              <v-card-text class="text-left pt-0">
                <v-row class="pt-5">
                  <v-col :md="8">
                    <label>{{ $t('label.rsa_key_size') }}</label>
                    <v-slider
                      v-model="form.rsa_key_size"
                      max="8192"
                      step="2048"
                      min="0"
                      track-color="#E2E2E2"
                    >
                      <template v-slot:append>
                        <v-text-field
                          v-model="form.rsa_key_size"
                          class="mt-0 pt-0"
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
                  <v-col :md="8">
                    <label>{{ $t('label.password_duration') }}</label>
                    <v-slider
                      v-model="form.password_duration"
                      max="365"
                      step="1"
                      min="1"
                      track-color="#E2E2E2"
                    >
                      <template v-slot:append>
                        <v-text-field
                          v-model="form.password_duration"
                          class="mt-0 pt-0"
                          hide-details
                          single-line
                          type="number"
                          style="width: 60px"
                        />
                      </template>
                    </v-slider>
                  </v-col>
                </v-row>
                <h2 class="mb-2">{{ $t("label.users_password_policy") }}</h2>
                <v-row dense>
                  <v-col class="text-left" :md="8">
                    <label>{{ $t('label.password_length') }}</label>
                    <v-slider
                      v-model="form.password_policy.length"
                      max="100"
                      min="0"
                      track-color="#E2E2E2"
                    >
                      <template v-slot:append>
                        <v-text-field
                          v-model="form.password_policy.length"
                          class="mt-0 pt-0"
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
                  <v-col class="text-left" :md="8">
                    <label>{{ $t('label.password_upper') }}</label>
                    <v-slider
                      v-model="form.password_policy.uppercase"
                      :max="form.password_policy.length"
                      min="0"
                      track-color="#E2E2E2"
                    >
                      <template v-slot:append>
                        <v-text-field
                          v-model="form.password_policy.uppercase"
                          class="mt-0 pt-0"
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
                  <v-col class="text-left" :md="8">
                    <label>{{ $t('label.password_number') }}</label>
                    <v-slider
                      v-model="form.password_policy.numbers"
                      :max="form.password_policy.length - form.password_policy.uppercase"
                      min="0"
                      track-color="#E2E2E2"
                    >
                      <template v-slot:append>
                        <v-text-field
                          v-model="form.password_policy.numbers"
                          class="mt-0 pt-0"
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
                  <v-col class="text-left" :md="8">
                    <label>{{ $t('label.password_special') }}</label>
                    <v-slider
                      v-model="form.password_policy.special"
                      :max="form.password_policy.length - (form.password_policy.uppercase + form.password_policy.numbers)"
                      min="0"
                      track-color="#E2E2E2"
                    >
                      <template v-slot:append>
                        <v-text-field
                          v-model="form.password_policy.special"
                          class="mt-0 pt-0"
                          hide-details
                          single-line
                          type="number"
                          style="width: 60px"
                        />
                      </template>
                    </v-slider>
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" :loading="isLoadingConfigForm" type="submit">{{ $t('button.save') }}</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-form>
        </v-tab-item>
        <v-tab-item key="tab-registration">
          <v-form @submit.prevent="saveConfig">
              <v-card flat>
                  <v-card-text class="text-left pt-0">
                    <v-row dense>
                      <v-col :md="6">
                        <v-switch
                          class="mb-2"
                          v-model="form.allow_self_registration"
                          :label="$t('label.allow_self_registration')"
                          :hint="$t('help.allow_self_registration')"
                          persistent-hint
                        />
                      </v-col>
                    </v-row>
                    <v-row dense v-if="form.allow_self_registration">
                      <v-col :md="6">
                        <v-combobox
                          v-model="form.allowed_email_addresses"
                          :items="[]"
                          append-icon=""
                          :label="$t('label.allowed_email_addresses')"
                          :hint="$t('help.allowed_email_addresses')"
                          persistent-hint
                          multiple
                          chips
                        >
                          <template v-slot:selection="{ attrs, item, parent, selected }">
                            <v-chip
                              v-bind="attrs"
                              color="primary"
                              :input-value="selected"
                              label
                              small
                            >
                              <span class="pr-2">
                                {{ item }}
                              </span>
                              <v-icon
                                small
                                @click="parent.selectItem(item)"
                              >
                                $delete
                              </v-icon>
                            </v-chip>
                          </template>
                        </v-combobox>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" :loading="isLoadingConfigForm" type="submit">{{ $t('button.save') }}</v-btn>
                    <v-spacer></v-spacer>
                  </v-card-actions>
              </v-card>
          </v-form>
        </v-tab-item>
        <v-tab-item key="tab-pro" v-if="is_pro">
          <v-form @submit.prevent="saveProConfig">
            <v-card flat>
              <v-card-text class="text-left pt-0">
                <v-row class="">
                  <v-col :md="8">
                    <v-switch
                      v-model="form_pro.enforce_totp"
                      :label="$t('label.enforce_totp')"
                      :hint="$t('help.enforce_totp')"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" :loading="isLoadingProForm" type="submit">{{ $t('button.save') }}</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-form>
        </v-tab-item>
        <v-tab-item key="tab-recovery" v-if="is_pro">
          <recovery />
        </v-tab-item>
      </v-tabs-items>
    </v-card>
  </v-container>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import Recovery from './components/Recovery.vue'
import http from "@/utils/http"


export default defineComponent({
  components: { Recovery },
  data: () => ({
    isLoadingConfigForm: false,
    isLoadingProForm: false,
    tab: 0,
    is_pro: false,

    form_pro: {
      enforce_totp: false
    },

    form: {
      password_policy: {
        length: 12,
        uppercase: 1,
        numbers: 1,
        special: 1  
      },
      rsa_key_size: 4096,
      password_duration: 100,
      allow_self_registration: false,
      allowed_email_addresses: []
    }
  }),

  beforeMount() {
    this.is_pro = this.$store.state.pro
  },

  mounted() {
      this.getConfig()
      this.getProConfig()
  },

  methods: {
    getConfig() {
      http.get("/api/v1/config/").then((response) => {
        this.form.password_policy = response.data.password_policy
        this.form.rsa_key_size = response.data.rsa_key_size
        this.form.password_duration = response.data.password_duration
        this.form.enforce_totp = response.data.enforce_totp
        this.form.allow_self_registration = response.data.allow_self_registration
        this.form.allowed_email_addresses = response.data.allowed_email_addresses
      })
    },

    getProConfig() {
      http.get("/pro/api/v1/config/").then((response) => {
        this.form_pro.enforce_totp = response.data.enforce_totp
      })
    },

    saveConfig() {
      this.isLoadingConfigForm = true
      http.post("/api/v1/config/", this.form).then(() => {
        this.$toast.success(this.$t("success.configuration_saved"))
        this.getConfig()
      }).then(() => {
        this.isLoadingConfigForm = false
      })
    },

    saveProConfig() {
      this.isLoadingProForm = true
      http.post("/pro/api/v1/config/", this.form_pro).then(() => {
        this.$toast.success(this.$t("success.configuration_saved"))
        this.getProConfig()
      }).then(() => {
        this.isLoadingProForm = false
      })
    }
  }
})
</script>
