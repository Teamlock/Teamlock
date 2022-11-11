<template>
    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      :nudge-width="300"
      offset-x
      left
    >
      <template v-slot:activator="{ on, attrs }">
        <v-icon
            v-on="on"
            v-bind="attrs"
            @click="getProperties"
        >
            mdi-auto-fix
        </v-icon>
      </template>

      <v-card>
        <v-list>
          <v-list-item>
            <v-list-item-icon>
                <v-icon>mdi-lock</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ $t("title.password_generator") }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>

        <v-divider></v-divider>

        <v-list>
            <v-list-item>
                <v-text-field
                    :label="$t('label.password')"
                    readonly
                    :loading="passwordLoading"
                    v-model="password"
                >
                    <template v-slot:append>
                        <v-btn
                            icon
                            @click="generatePassword"
                        >
                            <v-icon>mdi-refresh</v-icon>
                        </v-btn>
                    </template>
                </v-text-field>
            </v-list-item>
            <v-list-item dense>
                <v-list-item-content>
                    <v-list-item-title>{{ $t("label.min_length") }} : {{ length }}</v-list-item-title>
                    <v-slider
                        dense
                        v-model="length"
                        thumb-label
                        :min="policy['length']"
                        max="100"
                        @end="generatePassword"
                    >
                    </v-slider>
                </v-list-item-content>
            </v-list-item>
            <v-list-item dense>
                <v-list-item-content>
                    <v-list-item-title>{{ $t("label.min_uppercase") }} : {{ uppercase }}</v-list-item-title>
                    <v-slider
                        dense
                        v-model="uppercase"
                        thumb-label
                        :min="policy.uppercase"
                        :max="length"
                        @end="generatePassword"
                    >
                    </v-slider>
                </v-list-item-content>
            </v-list-item>
            <v-list-item dense>
                <v-list-item-content>
                    <v-list-item-title>{{ $t("label.min_numbers") }} : {{ numbers }}</v-list-item-title>
                    <v-slider
                        dense
                        v-model="numbers"
                        thumb-label
                        :min="policy.numbers"
                        :max="length"
                        @end="generatePassword"
                    >
                    </v-slider>
                </v-list-item-content>
            </v-list-item>
            <v-list-item dense>
                <v-list-item-content>
                    <v-list-item-title>{{ $t("label.min_special") }} : {{ special }}</v-list-item-title>
                    <v-slider
                        dense
                        v-model="special"
                        thumb-label
                        :min="policy.special"
                        :max="length"
                        @end="generatePassword"
                    >
                    </v-slider>
                </v-list-item-content>
            </v-list-item>
        </v-list>
        

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn
            text
            @click="menu = false"
          >
            {{ $t("button.cancel")}}
          </v-btn>
          <v-btn
            color="primary"
            text
            @click="sendPassword"
          >
            {{ $t("button.validate")}}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-menu>
</template>
<script>
import { defineComponent } from '@vue/composition-api';
import http from "@/utils/http";
import { mapGetters } from 'vuex';

export default defineComponent({
    name: "PasswordGenerator",

    data : () => ({
        menu: false,
        password: "",
        passwordLoading: false,
        length: 12,
        uppercase: 1,
        numbers: 1,
        special: 1
    }),

    computed: {
        ...mapGetters({
          policy: 'getPasswordPolicy',
          folder_id: "getFolder"
        })
    },

    methods:{
        getProperties(){
            ["length","uppercase","numbers","special"].forEach(prop => {
                this[prop] = this.policy[prop];
            });
            this.generatePassword();
        },
        generatePassword(){
            this.passwordLoading = true;
            this.fakePassword(3);
            const data = {
                length: this.length,
                uppercase: this.uppercase,
                numbers: this.numbers,
                special: this.special,
            };
            const query = {
                    folder_id: this.folder_id
            };


            http.post(`/api/v1/secret/generate`, data, {params: query}).then((res) => {
                this.passwordLoading = false;
                this.password = res.data;
            })
        },

        sendPassword(){
            this.$emit("password", this.password);
            this.menu = false;
        },

        fakePassword(count=1){
            let passwordKeys = "";
            let password = "";
            passwordKeys += "abcdefghijklmnopqrstuvwxyz";
            if (this.uppercase) passwordKeys += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
            if (this.numbers) passwordKeys += "1234567890";
            if (this.special) passwordKeys += "&#?!%*$";

            for (let i = 0; i < this.length; i++) {
                const index = Math.floor(Math.random() * passwordKeys.length);
                password += passwordKeys[index];
            }
            this.password = password;
            if (--count > 0) setTimeout(this.fakePassword, 50, count);
        }
    }    
})
</script>
