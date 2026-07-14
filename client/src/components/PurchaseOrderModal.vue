<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{
                mode === "create"
                  ? "Create Purchase Order"
                  : "Purchase Order Details"
              }}
            </h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path
                  d="M15 5L5 15M5 5L15 15"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="shortage-header">
              <div class="shortage-title-section">
                <h4 class="item-name">{{ backlogItem.item_name }}</h4>
                <div class="item-sku">SKU: {{ backlogItem.item_sku }}</div>
              </div>
              <span class="priority-badge" :class="backlogItem.priority">
                {{ backlogItem.priority }} Priority
              </span>
            </div>

            <div class="shortage-summary">
              <div class="summary-card danger">
                <div class="summary-label">Shortage Amount</div>
                <div class="summary-value">{{ shortage }} units</div>
              </div>
              <div class="summary-card warning">
                <div class="summary-label">Days Delayed</div>
                <div class="summary-value">
                  {{ backlogItem.days_delayed }} days
                </div>
              </div>
            </div>

            <!-- Create mode: form -->
            <form
              v-if="mode === 'create'"
              class="po-form"
              @submit.prevent="submitForm"
            >
              <div class="form-grid">
                <div class="form-field">
                  <label class="form-label" for="supplier-name"
                    >Supplier Name</label
                  >
                  <input
                    id="supplier-name"
                    v-model="form.supplier_name"
                    type="text"
                    class="form-input"
                    :class="{ 'has-error': fieldErrors.supplier_name }"
                    required
                    @input="fieldErrors.supplier_name = false"
                  />
                </div>

                <div class="form-field">
                  <label class="form-label" for="quantity">Quantity</label>
                  <input
                    id="quantity"
                    v-model.number="form.quantity"
                    type="number"
                    min="1"
                    class="form-input"
                    :class="{ 'has-error': fieldErrors.quantity }"
                    required
                    @input="fieldErrors.quantity = false"
                  />
                </div>

                <div class="form-field">
                  <label class="form-label" for="unit-cost">Unit Cost</label>
                  <input
                    id="unit-cost"
                    v-model.number="form.unit_cost"
                    type="number"
                    min="0"
                    step="0.01"
                    class="form-input"
                    :class="{ 'has-error': fieldErrors.unit_cost }"
                    required
                    @input="fieldErrors.unit_cost = false"
                  />
                </div>

                <div class="form-field">
                  <label class="form-label" for="expected-delivery-date"
                    >Expected Delivery Date</label
                  >
                  <input
                    id="expected-delivery-date"
                    v-model="form.expected_delivery_date"
                    type="date"
                    class="form-input"
                    :class="{ 'has-error': fieldErrors.expected_delivery_date }"
                    required
                    @input="fieldErrors.expected_delivery_date = false"
                  />
                </div>

                <div class="form-field form-field-full">
                  <label class="form-label" for="notes">Notes</label>
                  <textarea
                    id="notes"
                    v-model="form.notes"
                    class="form-textarea"
                    rows="3"
                  ></textarea>
                </div>
              </div>

              <div v-if="validationWarning" class="form-warning">
                {{ validationWarning }}
              </div>
              <div v-if="submitError" class="form-error">{{ submitError }}</div>
            </form>

            <!-- View mode: read-only PO details -->
            <div v-else>
              <div v-if="loadingPo" class="po-loading">
                Loading purchase order...
              </div>
              <div v-else-if="loadError" class="form-error">
                {{ loadError }}
              </div>
              <div v-else-if="purchaseOrder" class="info-grid">
                <div class="info-item">
                  <div class="info-label">Supplier</div>
                  <div class="info-value">
                    {{ purchaseOrder.supplier_name }}
                  </div>
                </div>

                <div class="info-item">
                  <div class="info-label">Quantity</div>
                  <div class="info-value">
                    {{ purchaseOrder.quantity }} units
                  </div>
                </div>

                <div class="info-item">
                  <div class="info-label">Unit Cost</div>
                  <div class="info-value">
                    ${{ Number(purchaseOrder.unit_cost).toFixed(2) }}
                  </div>
                </div>

                <div class="info-item">
                  <div class="info-label">Expected Delivery</div>
                  <div class="info-value">
                    {{ formatDate(purchaseOrder.expected_delivery_date) }}
                  </div>
                </div>

                <div class="info-item">
                  <div class="info-label">Status</div>
                  <div class="info-value">
                    <span class="badge">{{ purchaseOrder.status }}</span>
                  </div>
                </div>

                <div class="info-item">
                  <div class="info-label">Created Date</div>
                  <div class="info-value">
                    {{ formatDate(purchaseOrder.created_date) }}
                  </div>
                </div>

                <div
                  class="info-item form-field-full"
                  v-if="purchaseOrder.notes"
                >
                  <div class="info-label">Notes</div>
                  <div class="info-value">{{ purchaseOrder.notes }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="close">Close</button>
            <button
              v-if="mode === 'create'"
              class="btn-primary"
              :disabled="submitting"
              @click="submitForm"
            >
              {{ submitting ? "Creating..." : "Create Purchase Order" }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { api } from "../api";

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  backlogItem: {
    type: Object,
    default: null,
  },
  mode: {
    type: String,
    default: "create",
  },
});

const emit = defineEmits(["close", "po-created"]);

const shortage = computed(() => {
  if (!props.backlogItem) return 0;
  return (
    props.backlogItem.quantity_needed - props.backlogItem.quantity_available
  );
});

const form = reactive({
  supplier_name: "",
  quantity: 0,
  unit_cost: 0,
  expected_delivery_date: "",
  notes: "",
});

const submitting = ref(false);
const submitError = ref(null);
const validationWarning = ref(null);
const fieldErrors = reactive({
  supplier_name: false,
  quantity: false,
  unit_cost: false,
  expected_delivery_date: false,
});

const purchaseOrder = ref(null);
const loadingPo = ref(false);
const loadError = ref(null);

const resetForm = () => {
  if (!props.backlogItem) return;
  form.supplier_name = "";
  form.quantity = Math.max(
    props.backlogItem.quantity_needed - props.backlogItem.quantity_available,
    1,
  );
  form.unit_cost = 0;
  form.expected_delivery_date = "";
  form.notes = "";
  submitError.value = null;
  validationWarning.value = null;
  fieldErrors.supplier_name = false;
  fieldErrors.quantity = false;
  fieldErrors.unit_cost = false;
  fieldErrors.expected_delivery_date = false;
};

// Validates required fields before submit. Returns true if the form is valid.
// A $0 unit cost is treated as invalid since a real PO always has a cost.
const validateForm = () => {
  fieldErrors.supplier_name = !form.supplier_name || !form.supplier_name.trim();
  fieldErrors.quantity = !(Number(form.quantity) > 0);
  fieldErrors.unit_cost = !(Number(form.unit_cost) > 0);
  fieldErrors.expected_delivery_date = !form.expected_delivery_date;

  return !(
    fieldErrors.supplier_name ||
    fieldErrors.quantity ||
    fieldErrors.unit_cost ||
    fieldErrors.expected_delivery_date
  );
};

const loadPurchaseOrder = async () => {
  if (!props.backlogItem) return;
  loadingPo.value = true;
  loadError.value = null;
  purchaseOrder.value = null;
  try {
    purchaseOrder.value = await api.getPurchaseOrderByBacklogItem(
      props.backlogItem.id,
    );
  } catch (err) {
    loadError.value = "Failed to load purchase order details";
    console.error(err);
  } finally {
    loadingPo.value = false;
  }
};

// When the modal opens (or the target item/mode changes), initialize form or fetch existing PO
watch(
  () => [props.isOpen, props.backlogItem, props.mode],
  () => {
    if (!props.isOpen || !props.backlogItem) return;
    if (props.mode === "create") {
      resetForm();
    } else {
      loadPurchaseOrder();
    }
  },
  { immediate: true },
);

const submitForm = async () => {
  if (!props.backlogItem) return;
  submitError.value = null;

  if (!validateForm()) {
    validationWarning.value =
      "Please fill in all required fields before creating the purchase order.";
    return;
  }
  validationWarning.value = null;

  submitting.value = true;
  try {
    const createdPo = await api.createPurchaseOrder({
      backlog_item_id: props.backlogItem.id,
      supplier_name: form.supplier_name,
      quantity: form.quantity,
      unit_cost: form.unit_cost,
      expected_delivery_date: form.expected_delivery_date,
      notes: form.notes || undefined,
    });
    emit("po-created", createdPo);
  } catch (err) {
    submitError.value = "Failed to create purchase order";
    console.error(err);
  } finally {
    submitting.value = false;
  }
};

const close = () => {
  emit("close");
};

const formatDate = (dateString) => {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return "N/A";
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.close-button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.shortage-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.shortage-title-section {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
}

.item-sku {
  font-size: 0.875rem;
  color: #64748b;
  font-family: "Monaco", "Courier New", monospace;
}

.priority-badge {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  flex-shrink: 0;
}

.priority-badge.high {
  background: #fecaca;
  color: #991b1b;
}

.priority-badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.priority-badge.low {
  background: #dbeafe;
  color: #1e40af;
}

.shortage-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-card {
  padding: 1.25rem;
  border-radius: 10px;
  border: 2px solid;
}

.summary-card.danger {
  border-color: #fecaca;
  background: #fef2f2;
}

.summary-card.warning {
  border-color: #fed7aa;
  background: #fffbeb;
}

.summary-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.summary-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #0f172a;
}

.summary-card.danger .summary-value {
  color: #dc2626;
}

.summary-card.warning .summary-value {
  color: #f59e0b;
}

.po-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.form-field-full {
  grid-column: 1 / -1;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.form-input,
.form-textarea {
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.938rem;
  color: #0f172a;
  font-family: inherit;
  transition: border-color 0.15s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #2563eb;
}

.form-textarea {
  resize: vertical;
}

.form-input.has-error,
.form-textarea.has-error {
  border-color: #f59e0b;
}

.form-warning {
  padding: 0.75rem 1rem;
  background: #fffbeb;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  color: #f59e0b;
  font-size: 0.875rem;
  font-weight: 500;
}

.form-error {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.875rem;
  font-weight: 500;
}

.po-loading {
  padding: 2rem 0;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.info-value {
  font-size: 0.938rem;
  color: #0f172a;
  font-weight: 500;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 6px;
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: capitalize;
  background: #dbeafe;
  color: #1e40af;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
