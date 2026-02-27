import { useEffect, useState } from 'react'
import { Plus, Search, Users } from 'lucide-react'
import api from '../services/api'

export default function Clients() {
  const [clients, setClients] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ code_client: '', raison_sociale: '', telephone: '', email: '', ville: '' })

  const load = () => {
    api.get('/clients', { params: { page, search: search || undefined } }).then((r) => {
      setClients(r.data.items)
      setTotal(r.data.total)
    })
  }

  useEffect(load, [page, search])

  const handleCreate = async (e) => {
    e.preventDefault()
    await api.post('/clients', form)
    setShowForm(false)
    setForm({ code_client: '', raison_sociale: '', telephone: '', email: '', ville: '' })
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Rechercher un client..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
          />
        </div>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
          <Plus size={18} /> Nouveau client
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl shadow-sm border p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <input placeholder="Code client *" required value={form.code_client} onChange={(e) => setForm({ ...form, code_client: e.target.value })} className="px-3 py-2 border rounded-lg" />
          <input placeholder="Raison sociale *" required value={form.raison_sociale} onChange={(e) => setForm({ ...form, raison_sociale: e.target.value })} className="px-3 py-2 border rounded-lg" />
          <input placeholder="Téléphone" value={form.telephone} onChange={(e) => setForm({ ...form, telephone: e.target.value })} className="px-3 py-2 border rounded-lg" />
          <input placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="px-3 py-2 border rounded-lg" />
          <input placeholder="Ville" value={form.ville} onChange={(e) => setForm({ ...form, ville: e.target.value })} className="px-3 py-2 border rounded-lg" />
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">Créer</button>
        </form>
      )}

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 font-medium text-gray-600">Code</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600">Raison sociale</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600 hidden md:table-cell">Ville</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600 hidden md:table-cell">Téléphone</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600 hidden lg:table-cell">Email</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {clients.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-6 py-3 font-mono text-primary-600">{c.code_client}</td>
                <td className="px-6 py-3 font-medium">{c.raison_sociale}</td>
                <td className="px-6 py-3 hidden md:table-cell text-gray-500">{c.ville || '-'}</td>
                <td className="px-6 py-3 hidden md:table-cell text-gray-500">{c.telephone || '-'}</td>
                <td className="px-6 py-3 hidden lg:table-cell text-gray-500">{c.email || '-'}</td>
              </tr>
            ))}
            {clients.length === 0 && (
              <tr><td colSpan="5" className="px-6 py-12 text-center text-gray-400">
                <Users size={40} className="mx-auto mb-2 opacity-50" />
                Aucun client trouvé
              </td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{total} client(s)</span>
        <div className="flex gap-2">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-3 py-1 border rounded disabled:opacity-30">Précédent</button>
          <span className="px-3 py-1">Page {page}</span>
          <button onClick={() => setPage(page + 1)} disabled={clients.length < 50} className="px-3 py-1 border rounded disabled:opacity-30">Suivant</button>
        </div>
      </div>
    </div>
  )
}
