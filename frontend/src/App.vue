<template>
  <div class="mx-auto p-6 bg-gray-50 min-h-screen">
    <header class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Classificações Sugeridas</h1>
      <p class="text-gray-500">MLocks NERC (NFe Expense Receipt Classifier)</p>
    </header>

    <div class="flex gap-2 mb-4">
      <button @click="filtro = 'sugerido'" :class="btnClass(filtro === 'sugerido')"
        class="px-4 py-2 rounded transition-colors">
        Pendentes
      </button>
      <button @click="filtro = 'aprovado'" :class="btnClass(filtro === 'aprovado')"
        class="px-4 py-2 rounded transition-colors">
        Aprovados
      </button>
      <button @click="filtro = 'rejeitado'" :class="btnClass(filtro === 'rejeitado')"
        class="px-4 py-2 rounded transition-colors">
        Rejeitados
      </button>
    </div>

    <div class="bg-white rounded-xl shadow overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-100 text-left text-sm">
          <tr>
            <th class="p-3">ID</th>
            <th>Descrição</th>
            <th>Valor</th>
            <th class="p-3">Categoria</th>
            <th>Origem</th>
            <th class="p-3">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in itens" :key="item.id" class="border-t hover:bg-gray-50">
            <td class="p-3">{{ item.id }}</td>
            <td class="max-w-xs truncate" :title="item.descricao">{{ item.descricao }}</td>
            <td class="whitespace-nowrap">R$ {{ item.valor }}</td>
            <td class="p-3">
              <div class="font-medium">{{ item.categoria }}</div>
              <div class="text-xs text-gray-500">{{ item.justificativa }}</div>
            </td>
            <td>
              <span class="px-2 py-1 text-xs rounded" :class="tagClass(item.origem)">
                {{ item.origem }}
              </span>
            </td>
            <td class="p-3">
              <template v-if="item.status === 'sugerido'">
                <button @click="aprovar(item.id)" class="text-green-600 hover:underline">Aprovar</button>
                <button @click="rejeitar(item.id)" class="text-red-600 hover:underline">Rejeitar</button>
              </template>
              <span v-else class="text-gray-400 capitalize">{{ item.status }}</span>
            </td>
          </tr>
          <tr v-if="itens.length === 0">
            <td colspan="6" class="p-6 text-center text-gray-500">Nenhum registro encontrado.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex justify-between items-center mt-4 text-sm text-gray-600">
      <button @click="pagina--" :disabled="pagina === 1"
        class="px-3 py-1 border rounded disabled:opacity-50 hover:bg-gray-100">
        Anterior
      </button>
      <span>Página {{ pagina }} de {{ paginas || 1 }}</span>
      <button @click="pagina++" :disabled="pagina === paginas || paginas === 0"
        class="px-3 py-1 border rounded disabled:opacity-50 hover:bg-gray-100">
        Próxima
      </button>
    </div>
  </div>
</template>

<script setup>
/*
 * The MIT License
 *
 * Copyright 2026 Juliano Maciel.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
import { ref, watch, computed } from 'vue'

const itens = ref([])
const filtro = ref('sugerido')
const pagina = ref(1)
const total = ref(0)
const limit = 10

// Use Vite environment variables
const API = import.meta.env.API_URL || 'http://localhost:8000'

const paginas = computed(() => Math.ceil(total.value / limit))

async function carregar() {
  try {
    const r = await fetch(`${API}/classificacoes?status=${filtro.value}&page=${pagina.value}&limit=${limit}`)
    const data = await r.json()
    itens.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error("Erro ao carregar dados:", error)
  }
}

async function aprovar(id) {
  await fetch(`${API}/classificacoes/${id}/aprovar`, { method: 'POST' })
  carregar()
}

async function rejeitar(id) {
  await fetch(`${API}/classificacoes/${id}/rejeitar`, { method: 'POST' })
  carregar()
}

const btnClass = (ativo) => ativo ? 'bg-blue-600 text-white shadow' : 'bg-white border text-gray-700 hover:bg-gray-50'
const tagClass = (o) => ({ mock: 'bg-gray-200', ollama: 'bg-purple-200', vertex: 'bg-green-200' }[o] || 'bg-gray-200')

// Reset page to 1 when changing filters, and trigger load
watch(filtro, () => {
  pagina.value = 1
})

watch([filtro, pagina], carregar, { immediate: true })
</script>