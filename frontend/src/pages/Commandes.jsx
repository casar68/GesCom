import { useEffect, useState } from 'react'
import { Search, ShoppingCart } from 'lucide-react'
import api from '../services/api'

const STATUT_COLORS = {
  brouillon: 'bg-gray-100 text-gray-700',
  validee: 'bg-blue-100 text-blue-700',
  en_preparation: 'bg-yellow-100 text-yellow-700',
  preparee: 'bg-indigo-100 text-indigo-700',
  expediee: 'bg-purple-100 text-purple-700',
  livree: 'bg-green-100 text-green-700',
  facturee: 'bg-teal-100 text-teal-700',
  annulee: 'bg-red-100 text-red-700',
}

export default function Commandes() {
  const [commandes, setCommandes] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)

  const load = () => {
    api.get('/commandes', { params: { page } }).then((r) => {
      setCommandes(r.data.items)
      setTotal(r.data.total)
    })
  }

  useEffect(load, [page])

  const fmt = (n) => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(n)
  const fmtDate = (d) => new Date(d).toLocaleDateString('fr-FR')

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 font-medium text-gray-600">N. Commande</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600">Date</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600">Statut</th>
              <th className="text-right px-6 py-3 font-medium text-gray-600">Total TTC</th>
              <th className="text-right px-6 py-3 font-medium text-gray-600 hidden md:table-cell">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {commandes.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-6 py-3 font-mono text-primary-600">{c.numero}</td>
                <td className="px-6 py-3 text-gray-500">{fmtDate(c.date_commande)}</td>
                <td className="px-6 py-3">
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${STATUT_COLORS[c.statut] || 'bg-gray-100'}`}>
                    {c.statut}
                  </span>
                </td>
                <td className="px-6 py-3 text-right font-medium">{fmt(c.total_ttc)}</td>
                <td className="px-6 py-3 text-right hidden md:table-cell space-x-2">
                  {c.statut === 'brouillon' && (
                    <button onClick={() => api.post(`/commandes/${c.id}/valider`).then(load)} className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded hover:bg-blue-100">
                      Valider
                    </button>
                  )}
                  {['validee', 'en_preparation', 'preparee'].includes(c.statut) && (
                    <button onClick={() => api.post(`/commandes/${c.id}/facturer`).then(load)} className="text-xs bg-green-50 text-green-600 px-2 py-1 rounded hover:bg-green-100">
                      Facturer
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {commandes.length === 0 && (
              <tr><td colSpan="5" className="px-6 py-12 text-center text-gray-400">
                <ShoppingCart size={40} className="mx-auto mb-2 opacity-50" />
                Aucune commande
              </td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{total} commande(s)</span>
        <div className="flex gap-2">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-3 py-1 border rounded disabled:opacity-30">Précédent</button>
          <span className="px-3 py-1">Page {page}</span>
          <button onClick={() => setPage(page + 1)} disabled={commandes.length < 50} className="px-3 py-1 border rounded disabled:opacity-30">Suivant</button>
        </div>
      </div>
    </div>
  )
}
