import { useEffect, useState } from 'react'
import { FileText, Download } from 'lucide-react'
import api from '../services/api'

const STATUT_COLORS = {
  brouillon: 'bg-gray-100 text-gray-700',
  emise: 'bg-blue-100 text-blue-700',
  envoyee: 'bg-indigo-100 text-indigo-700',
  payee_partiellement: 'bg-yellow-100 text-yellow-700',
  payee: 'bg-green-100 text-green-700',
  en_retard: 'bg-red-100 text-red-700',
  annulee: 'bg-gray-200 text-gray-500',
  avoir: 'bg-orange-100 text-orange-700',
}

export default function Factures() {
  const [factures, setFactures] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)

  const load = () => {
    api.get('/factures', { params: { page } }).then((r) => {
      setFactures(r.data.items)
      setTotal(r.data.total)
    })
  }

  useEffect(load, [page])

  const fmt = (n) => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(n)
  const fmtDate = (d) => new Date(d).toLocaleDateString('fr-FR')

  const downloadPdf = async (id, numero) => {
    const res = await api.get(`/reporting/export/facture/${id}/pdf`, { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `facture_${numero}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 font-medium text-gray-600">N. Facture</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600">Date</th>
              <th className="text-left px-6 py-3 font-medium text-gray-600">Statut</th>
              <th className="text-right px-6 py-3 font-medium text-gray-600">Total TTC</th>
              <th className="text-right px-6 py-3 font-medium text-gray-600 hidden md:table-cell">Réglé</th>
              <th className="text-right px-6 py-3 font-medium text-gray-600">PDF</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {factures.map((f) => (
              <tr key={f.id} className="hover:bg-gray-50">
                <td className="px-6 py-3 font-mono text-primary-600">{f.numero}</td>
                <td className="px-6 py-3 text-gray-500">{fmtDate(f.date_facture)}</td>
                <td className="px-6 py-3">
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${STATUT_COLORS[f.statut] || 'bg-gray-100'}`}>
                    {f.statut}
                  </span>
                </td>
                <td className="px-6 py-3 text-right font-medium">{fmt(f.total_ttc)}</td>
                <td className="px-6 py-3 text-right hidden md:table-cell text-gray-500">{fmt(f.montant_regle)}</td>
                <td className="px-6 py-3 text-right">
                  <button onClick={() => downloadPdf(f.id, f.numero)} className="text-primary-600 hover:text-primary-800">
                    <Download size={16} />
                  </button>
                </td>
              </tr>
            ))}
            {factures.length === 0 && (
              <tr><td colSpan="6" className="px-6 py-12 text-center text-gray-400">
                <FileText size={40} className="mx-auto mb-2 opacity-50" />
                Aucune facture
              </td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{total} facture(s)</span>
        <div className="flex gap-2">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-3 py-1 border rounded disabled:opacity-30">Précédent</button>
          <span className="px-3 py-1">Page {page}</span>
          <button onClick={() => setPage(page + 1)} disabled={factures.length < 50} className="px-3 py-1 border rounded disabled:opacity-30">Suivant</button>
        </div>
      </div>
    </div>
  )
}
