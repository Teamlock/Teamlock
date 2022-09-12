<template>
  <span>
    <v-text-field
      @input="update('endpoint_url', $event)"
      :value="local.endpoint_url"
      :label="$t('label.s3_endpoint')"
    />
    <v-text-field
      @input="update('access_key', $event)"
      :value="local.access_key"
      :label="$t('label.s3_access_key')"
    />
    <v-text-field
      @input="update('secret_key', $event)"
      :value="local.secret_key"
      :label="$t('label.s3_secret_key')"
    />
    <v-text-field
      @input="update('region_name', $event)"
      v-model="local.region_name"
      :label="$t('label.s3_region_name')"
    />
    <v-text-field
      @input="update('bucket_name', $event)"
      v-model="local.bucket_name"
      :label="$t('label.s3_bucket_name')"
    />
  </span>
</template>

<script>
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  props: ['value'],
  data: () => ({
    is_loading: false
  }),

  computed: {
    local() {
      if (Object.keys(this.value).length) {
        return this.value
      } else {
        return {
          endpoint_url: "",
          access_key: "",
          secret_key: "",
          region_name: "",
          bucket_name: ""
        }
      }
    },
  },

  methods: {
    update(key, value) {
      this.$emit('input', { ...this.local, [key]: value })
    }
  }
})
</script>
