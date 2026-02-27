import { useEffect, useState } from 'react'
import { Plus, Search, Package } from 'lucide-react'
import api from '../services/api'

export default function Articles() {
  const [articles, setArticles] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ reference: '', designation: '', famille: '', prix_vente_ht: '', stock_actuel: 0 })

  const load = () => {
    api.get('/articles', { params: { page, search: search || undefined } }).then((r) => {
      setArticles(r.data.items)
      setTotal(r.data.total)
    })
  }

  useEffect(load, [page, search])

  const handleCreate = async (e) => {
    e.preventDefault()
    await api.post('/articles', { ...form, prix_vente_ht: form.prix_vente_ht || '0' })
    setShowForm(false)
    setForm({ reference: '', designation: '', famille: '', prix_vente_ht: '', stock_actuel: 0 })
    load()
  }

  const fmt = (n) => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(n)

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Rechercher un article..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
          />
        </div>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
          <Plus size={18} /> Nouvel article
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl shadow-sm border p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <input placeholder="Référence *" required value={form.reference} onChange={(e) => setForm({ ...form, reference: e.target.value })} className="px-3 py-2 border rounded-lg" />
          <input placeholder="Désignation *" required value={form.designation} onChange={(e) => setForm({ ...form, designation: e.target.value })} className="px-3 py-2 border rounded-lg" />
          <input placeholder="Famille" value={form.famille} onChange={(e) => setForm({ ...form, famille: e.target.value })} className="px-3 py-2 border rounded-lg" />
          <input placeholder="Prix vente HT" type="number" step="0.01" value={form.prix_vente_ht} onChange={(e) => setForm({ ...form, prix_vente_ht: e.target.value })} className="px-3 py-2 border rounded-lg" />
          <input placeholder="Stock initial" type="number" value={form.stock_actuel} onChange={(e) => setForm({ ...form, stock_actuel: parseInt(e.target.value) || 0 })} className="px-3 py-2 border rounded-lg" />
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">Créer</button>
        </form>
      )}

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 font-medium text-gray-600">Référence</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600">Désignation</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600 hidden md:table-cell">Famille</th>
              <th className="text-right px-6 py-3 font-medium text-gray-600">Prix HT</th>
              <th className="text-right px-6 py-3 font-medium text-gray-600">Stock</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {articles.map((a) => (
              <tr key={a.id} className="hover:bg-gray-50">
                <td className="px-6 py-3 font-mono text-primary-600">{a.reference}</td>
                <td className="px-6 py-3">{a.designation}</td>
                <td className="px-6 py-3 hidden md:table-cell text-gray-500">{a.famille || '-'}</td>
                <td className="px-6 py-3 text-right">{fmt(a.prix_vente_ht)}</td>
                <td className="px-6 py-3 text-right">
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${a.stock_actuel <= 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                    {a.stock_actuel}
                  </span>
                </td>
              </tr>
            ))}
            {articles.length === 0 && (
              <tr><td colSpan="5" className="px-6 py-12 text-center text-gray-400">
                <Package size={40} className="mx-auto mb-2 opacity-50" />
                Aucun article trouvé
              </td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{total} article(s)</span>
        <div className="flex gap-2">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-3 py-1 border rounded disabled:opacity-30">Précédent</button>
          <span className="px-3 py-1">Page {page}</span>
          <button onClick={() => setPage(page + 1)} disabled={articles.length < 50} className="px-3 py-1 border rounded disabled:opacity-30">Suivant</button>
        </div>
      </div>
    </div>
  )
}
