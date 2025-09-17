<!-- FlatpickrDateTime.vue -->
<template>
  <flat-pickr
    v-model="val"
    :config="config"
    class="form-control"
    style="max-width:320px"
  />
</template>

<script setup>
import { ref } from 'vue'
import FlatPickr from 'vue-flatpickr-component'
import 'flatpickr/dist/flatpickr.css'

const val = defineModel({ type: String, default: '' }) // ISO string by default

const config = {
  enableTime: false,
  time_24hr: true,
  dateFormat: 'Y-m-d',
  allowInput: true,
  // Add Today/Clear buttons
  onReady: (selectedDates, dateStr, instance) => {
    const footer = document.createElement('div')
    footer.style.display = 'flex'
    footer.style.justifyContent = 'space-between'
    footer.style.padding = '6px 8px'

    const todayBtn = document.createElement('button')
    todayBtn.type = 'button'
    todayBtn.textContent = 'Today'
    todayBtn.className = 'flatpickr-today'
    todayBtn.onclick = () => instance.setDate(new Date(), true)

    const clearBtn = document.createElement('button')
    clearBtn.type = 'button'
    clearBtn.textContent = 'Clear'
    clearBtn.className = 'flatpickr-clear'
    clearBtn.onclick = () => instance.clear()

    footer.append(todayBtn, clearBtn)
    instance.calendarContainer.appendChild(footer)
  }
}
</script>