<template>
  <span>
    <v-text-field
      @input="update('host', $event)"
      :value="local.host"
      :label="$t('label.sftp_host')"
    />
    <v-text-field
      @input="update('username', $event)"
      :value="local.username"
      :label="$t('label.sftp_username')"
    />
    <v-text-field
      @input="update('password', $event)"
      :value="local.password"
      :label="$t('label.sftp_password')"
      type="password"
    />
    <v-text-field
      @input="update('path', $event)"
      :value="local.path"
      :label="$t('label.sftp_path')"
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
          host: "",
          username: "",
          password: "",
          path: "/"
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
