import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, ShoppingCart, AlertTriangle, Users } from 'lucide-react'
import api from '../services/api'

const MOIS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

function StatCard({ title, value, icon: Icon, color }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon size={24} className="text-white" />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null)
  const [caMensuel, setCaMensuel] = useState([])

  useEffect(() => {
    api.get('/reporting/dashboard').then((r) => setDashboard(r.data)).catch(() => {})
    api.get('/reporting/ca-mensuel').then((r) => {
      setCaMensuel(r.data.map((d, i) => ({ ...d, name: MOIS[i] })))
    }).catch(() => {})
  }, [])

  if (!dashboard) return <div className="text-center py-12 text-gray-500">Chargement...</div>

  const fmt = (n) => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(n)

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="CA du mois" value={fmt(dashboard.ca_mois)} icon={TrendingUp} color="bg-green-500" />
        <StatCard title="Commandes du mois" value={dashboard.nb_commandes_mois} icon={ShoppingCart} color="bg-blue-500" />
        <StatCard title="Factures impayées" value={`${dashboard.factures_impayees_count} (${fmt(dashboard.factures_impayees_montant)})`} icon={AlertTriangle} color="bg-orange-500" />
        <StatCard title="Clients actifs" value={dashboard.nb_clients_actifs} icon={Users} color="bg-purple-500" />
      </div>

      {dashboard.articles_en_alerte > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center gap-3">
          <AlertTriangle className="text-amber-600" size={20} />
          <span className="text-amber-800 font-medium">{dashboard.articles_en_alerte} article(s) en alerte de stock</span>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Chiffre d'affaires mensuel</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={caMensuel}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(v) => fmt(v)} />
              <Bar dataKey="total_ttc" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
