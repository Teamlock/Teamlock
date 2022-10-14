<template>
  <v-chip-group v-if="item[field].value.length > 0" column>
    <v-chip
      v-for="(val, index) of items"
      @click="openUrl(val)"
      :key="index"
      class="mb-0"
      outlined
      label
      small
    >
      <v-icon small left>mdi-open-in-new</v-icon>
      <v-tooltip bottom v-model="tooltip_copy[index]">
        <template v-slot:activator="{ on, attrs }">
          <span
            class="cursor"
            v-on:click.stop
            v-on:dblclick.stop="copyData(val, index)"
            v-bind="attrs"
            v-on="on"
          >
            {{ val|str_limit(50) }}
          </span>
        </template>
        <span v-html="tooltipHTML" />
      </v-tooltip>
    </v-chip>
  </v-chip-group>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import secretMixin from "@/mixins/secrets"
import renderMixin from "@/mixins/render"

export default defineComponent({
  mixins: [secretMixin, renderMixin],

  props: {
    item: {
      type: Object,
      required: true
    },

    category: {
      type: String,
      required: true
    },

    field: {
      type: String,
      required: true
    }
  },

  data: (vm) => ({
    electron: false,
    tooltip_copy: [],
    tooltipHTML: vm.$t('tooltip.dblclick_copy')
  }),

  computed: {
    items() {
      // we don't show the if it's empty
      return this.item[this.field].value.filter(i => i !== '')
    }
  },

  beforeMount() {
    const userAgent = navigator.userAgent.toLowerCase();
    this.electron = userAgent.indexOf(' electron/') > -1
  },

  methods: {
    openUrl(val) {
      const regex = new RegExp("[a-z]*://.*")
      if (!regex.test(val)) {
        val = `http://${val}`
      }

      if (!this.electron) {
        window.open(val, "_blank")
      } else {
        window.ipc.send("OPEN", val);
      }

    },

    copySuccess(index) {
      setTimeout(() => {
        this.tooltipHTML = this.$t("help.copied")
        this.tooltip_copy[index] = true

        setTimeout(() => {
          this.tooltip_copy[index] = false

          setTimeout(() => {
            this.tooltipHTML = this.$t("tooltip.dblclick_copy")
          }, 500);
        }, 1000);
      }, 50);
    },

    copyData(value_to_copy, index) {
      if (!this.electron) {
        this.$copyText(value_to_copy)
        this.copySuccess(index)
        
      } else {
        window.ipc.send("COPY", value_to_copy)
        window.ipc.on("COPY", () => {
          this.tooltipHTML = this.$t("help.copied")
          this.copySuccess(index)
        })
      }
    },
  }
})
</script>
