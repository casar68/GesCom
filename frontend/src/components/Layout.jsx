import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, Package, Users, ShoppingCart,
  FileText, LogOut, Menu, X,
} from 'lucide-react'
import { useState } from 'react'

const nav = [
  { to: '/', label: 'Tableau de bord', icon: LayoutDashboard },
  { to: '/articles', label: 'Articles', icon: Package },
  { to: '/clients', label: 'Clients', icon: Users },
  { to: '/commandes', label: 'Commandes', icon: ShoppingCart },
  { to: '/factures', label: 'Factures', icon: FileText },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-30 w-64 bg-gray-900 text-white transform transition-transform lg:translate-x-0 lg:static lg:inset-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-700">
          <Link to="/" className="text-xl font-bold text-primary-400">GesCom</Link>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-gray-400">
            <X size={20} />
          </button>
        </div>

        <nav className="mt-6 px-3 space-y-1">
          {nav.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === to
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 w-full p-4 border-t border-gray-700">
          <div className="text-sm text-gray-400 mb-2">{user?.prenom} {user?.nom}</div>
          <button onClick={logout} className="flex items-center gap-2 text-sm text-gray-400 hover:text-white">
            <LogOut size={16} /> Déconnexion
          </button>
        </div>
      </aside>

      {/* Overlay mobile */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-20 bg-black/50 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main */}
      <main className="flex-1 min-w-0">
        <header className="h-16 bg-white border-b flex items-center px-6 lg:px-8">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden mr-4 text-gray-600">
            <Menu size={24} />
          </button>
          <h1 className="text-lg font-semibold text-gray-800">
            {nav.find((n) => n.to === location.pathname)?.label || 'GesCom'}
          </h1>
        </header>
        <div className="p-6 lg:p-8">{children}</div>
      </main>
    </div>
  )
}
