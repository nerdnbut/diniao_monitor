import { defineStore } from 'pinia';

interface FormState {
    name: string;
    ip: string;
    port: string;
    os: string;
    user: string;
    password: string;
}

export const useFormStore = defineStore('form', {
  state: (): FormState => ({
    name: '',
    ip: '',
    port: '',
    os: '',
    user: '',
    password: '',
  }),
  actions: {
    updateField(key: keyof FormState, value: string) {
      this[key] = value;
    },
    resetForm() {
      this.name = '';
      this.ip = '';
      this.port = '';
      this.os = '';
      this.user = '';
      this.password = '';
    }
  }
});
