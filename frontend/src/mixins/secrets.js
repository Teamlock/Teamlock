const secretMixin = {
  data: (vm) => ({
    trash: {},
    in_trash: false,
    is_trash: false,
    electron: false,
    tooltip_copy_password: {},
    tooltipSecretId: vm.$t("tooltip.copy_id"),
    startHeader: {
      text: vm.$t('label.name'),
      align: 'start',
      value: 'name',
    },
    endHeader: {
      text: vm.$t('label.actions'),
      align: 'start',
      value: 'actions',
      sortable: false,
      width: "150px",
      component: "ActionCell"
    },
    login: {
      headers: [
        {
          text: vm.$t('label.login'),
          align: 'start',
          value: 'login',
        },
        {
          text: vm.$t('label.password'),
          align: 'start',
          value: 'password',
          sortable: false,
          component: "SecretCell"
        },
        {
          text: vm.$t('label.url'),
          align: 'start',
          value: 'url',
          component: "UrlCell"
        },
        {
          text: vm.$t('label.ip'),
          align: 'start',
          value: 'ip',
        }
      ]
    },

    server: {
      headers: [
        {
          text: vm.$t('label.login'),
          align: 'start',
          value: 'login',
        },
        {
          text: vm.$t('label.password'),
          align: 'start',
          value: 'password',
          sortable: false,
          component: "SecretCell"
        },
        {
          text: vm.$t('label.ip'),
          align: 'start',
          value: 'ip',
        },
        {
          text: vm.$t('label.os'),
          align: 'start',
          value: 'os_type',
        }
      ]
    },

    bank: {
      headers: [
        {
          text: vm.$t('label.owner'),
          align: 'start',
          value: 'owner',
        },
        {
          text: vm.$t('label.bank_name'),
          align: 'start',
          value: 'bank_name',
        },
        {
          text: vm.$t('label.iban'),
          align: 'start',
          value: 'iban',
          sortable: false,
          component: "SecretCell"
        },
        {
          text: vm.$t('label.bic'),
          align: 'start',
          value: 'bic',
          sortable: false,
          component: "SecretCell"
        },
        {
          text: vm.$t('label.card_number'),
          align: 'start',
          value: 'card_number',
          sortable: false,
          component: "SecretCell"
        },
        {
          text: vm.$t('label.expiration_date'),
          align: 'start',
          value: 'expiration_date',
          sortable: false,
          component: "SecretCell"
        },
        {
          text: vm.$t('label.cvc'),
          align: 'start',
          value: 'cvc',
          sortable: false,
          component: "SecretCell"
        }
      ]
    },

    phone: {
      headers: [
        {
          text: vm.$t('label.number'),
          align: 'start',
          value: 'number',
        },
        {
          text: vm.$t('label.pin_code'),
          align: 'start',
          value: 'pin_code',
          sortable: false,
          component: "SecretCell"
        },
        {
          text: vm.$t('label.puk_code'),
          align: 'start',
          value: 'puk_code',
          sortable: false,
          component: "SecretCell"
        }
      ]
    }
  }),

  beforeMount() {
    const userAgent = navigator.userAgent.toLowerCase();
    this.electron = userAgent.indexOf(' electron/') > -1
  },

  methods: {
    copySuccess(message) {
      this.$toast.success(message, {
        closeOnClick: true,
        timeout: 3000,
        icon: true
      })

      if (this.electron) {
        setTimeout(() => {
          window.ipc.send("COPY", "")
        }, 30000);
      }
    },

    startDrag(event) {
      sessionStorage.setItem("draggedKey", event.srcElement.id)
    },

    endDrag() {
      sessionStorage.removeItem("draggedKey")
    },
  }
}

export default secretMixin