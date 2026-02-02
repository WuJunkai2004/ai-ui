<script setup>
import { ref, watch } from "vue";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import MultiSelect from "primevue/multiselect";
import DatePicker from "primevue/datepicker";
import Slider from "primevue/slider";
import ToggleSwitch from "primevue/toggleswitch";
import InputNumber from "primevue/inputnumber";
import Button from "primevue/button";

const props = defineProps({
  components: { type: Array, required: true },
});
const emit = defineEmits(["submit", "action"]);

const formData = ref({});

watch(
  () => props.components,
  (newVal) => {
    const data = {};
    if (newVal) {
      newVal.forEach((comp) => {
        if (comp.type === "RangeSlider") {
          data[comp.id] = [
            comp.default_min ?? comp.min ?? 0,
            comp.default_max ?? comp.max ?? 100,
          ];
        } else if (comp.type === "Switch") {
          data[comp.id] = comp.default_value || false;
        } else if (comp.type === "MultiSelect") {
          data[comp.id] = comp.default_values || [];
        } else if (comp.type === "Stepper") {
          data[comp.id] = comp.default_value || 0;
        } else {
          data[comp.id] = comp.default_value || null;
        }
      });
    }
    formData.value = data;
  },
  { immediate: true },
);

const submit = () => {
  emit("submit", formData.value);
};

const handleAction = (id, action) => {
  emit("action", { id, action });
};
</script>

<template>
  <div
    class="flex flex-column gap-3 p-3 border-200 border-round-xl bg-white shadow-1 my-2"
  >
    <div
      v-for="comp in components"
      :key="comp.id"
      class="flex flex-column gap-2"
    >
      <label :for="comp.id" class="font-medium text-900">{{
        comp.label
      }}</label>

      <InputText
        v-if="comp.type === 'Input'"
        :id="comp.id"
        v-model="formData[comp.id]"
        :placeholder="comp.placeholder"
      />

      <Select
        v-else-if="comp.type === 'Select'"
        :id="comp.id"
        v-model="formData[comp.id]"
        :options="comp.options"
        optionLabel="label"
        optionValue="value"
        :placeholder="comp.placeholder || '请选择'"
      />

      <MultiSelect
        v-else-if="comp.type === 'MultiSelect'"
        :id="comp.id"
        v-model="formData[comp.id]"
        :options="comp.options"
        optionLabel="label"
        optionValue="value"
        display="chip"
        :placeholder="comp.placeholder || '请选择多项'"
      />

      <div v-else-if="comp.type === 'RangeSlider'" class="px-2 pt-2 pb-1">
        <div class="flex justify-content-between mb-2 text-sm text-600">
          <span>{{ comp.min }}</span>
          <span class="font-bold text-primary"
            >{{ formData[comp.id]?.[0] }} - {{ formData[comp.id]?.[1] }}
            {{ comp.unit }}</span
          >
          <span>{{ comp.max }}</span>
        </div>
        <Slider
          v-model="formData[comp.id]"
          range
          :min="comp.min"
          :max="comp.max"
          :step="comp.step || 1"
        />
      </div>

      <ToggleSwitch
        v-else-if="comp.type === 'Switch'"
        :inputId="comp.id"
        v-model="formData[comp.id]"
      />

      <DatePicker
        v-else-if="comp.type === 'DatePicker'"
        :inputId="comp.id"
        v-model="formData[comp.id]"
        :selectionMode="comp.range ? 'range' : 'single'"
        dateFormat="yy-mm-dd"
        showIcon
        fluid
      />

      <InputNumber
        v-else-if="comp.type === 'Stepper'"
        :id="comp.id"
        v-model="formData[comp.id]"
        showButtons
        :min="comp.min"
        :max="comp.max"
        :step="comp.step || 1"
        fluid
      />

      <Button
        v-else-if="comp.type === 'Button'"
        :label="comp.label"
        :severity="
          comp.variant === 'danger'
            ? 'danger'
            : comp.variant === 'secondary'
              ? 'secondary'
              : 'primary'
        "
        @click="handleAction(comp.id, comp.action)"
        class="w-full"
      />

      <small v-if="comp.description" class="text-500">{{
        comp.description
      }}</small>
    </div>

    <div class="flex justify-content-end pt-3 border-top-1 border-100 mt-2">
      <Button
        label="提交信息"
        icon="pi pi-check"
        @click="submit"
        size="small"
      />
    </div>
  </div>
</template>
