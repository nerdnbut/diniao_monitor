import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useFormStore = defineStore('serverForm', () => {
  const name = ref('');
  const ip_address = ref('');
  const port = ref('');
  const operating_system = ref('');
  const status = ref('');
  const user = ref('');
  const password = ref('');

  const resetForm = () => {
    name.value = '';
    ip_address.value = '';
    port.value = '';
    operating_system.value = '';
    status.value = '';
    user.value = '';
    password.value = '';
  };

  return {
    name,
    ip_address,
    port,
    operating_system,
    status,
    user,
    password,
    resetForm,
  };
});
