import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Yardımcı: user kimliğini e-posta olarak taşımak için formattır.
export const formatUserEmail = (email) => (email || '').trim() || undefined
