import React, { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

const navLinkClass = (collapsed) => ({ isActive }) =>
  `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${collapsed ? 'justify-center' : ''} 
   ${isActive ? 'bg-gradient text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`

export default function PanelLayout() {
  const [collapsed, setCollapsed] = useState(false) // desktop
  const [mobileOpen, setMobileOpen] = useState(false) // mobile

  const SidebarContent = (
    <div className={`h-[70vh] rounded-2xl shadow-xl card glass border flex flex-col overflow-hidden ${collapsed ? 'w-16' : 'w-64'} transition-[width] duration-200`}>
      {/* Header / toggle */}
      <div className="p-3 flex items-center justify-between border-b border-gray-200/70">
        <div className={`${collapsed ? 'hidden' : 'block'}`}>
          <div className="text-sm font-semibold text-[var(--color-primary)]">CebimdekiVeri</div>
          <div className="text-[11px] text-gray-500">Kontrol Paneli</div>
        </div>
        <button
          className="w-8 h-8 inline-flex items-center justify-center rounded-lg hover:bg-gray-100"
          onClick={() => setCollapsed((v) => !v)}
          title={collapsed ? 'Genişlet' : 'Daralt'}
        >
          {collapsed ? '›' : '‹'}
        </button>
      </div>
      {/* Menu */}
      <nav className="px-2 py-3 text-sm flex-1 flex flex-col gap-1.5">
        <NavLink to="/" end className={navLinkClass(collapsed)} title="Dashboard">
          <span className="text-2xl leading-none">📊</span>
          <span className={`${collapsed ? 'hidden' : 'block'}`}>Dashboard</span>
        </NavLink>
        <NavLink to="/transactions" className={navLinkClass(collapsed)} title="İşlemler">
          <span className="text-2xl leading-none">📜</span>
          <span className={`${collapsed ? 'hidden' : 'block'}`}>İşlemler</span>
        </NavLink>
        <NavLink to="/chat" className={navLinkClass(collapsed)} title="AI Chat">
          <span className="text-2xl leading-none">🤖</span>
          <span className={`${collapsed ? 'hidden' : 'block'}`}>AI Chat</span>
        </NavLink>
        <NavLink to="/settings" className={navLinkClass(collapsed)} title="Ayarlar">
          <span className="text-2xl leading-none">🎨</span>
          <span className={`${collapsed ? 'hidden' : 'block'}`}>Ayarlar</span>
        </NavLink>
        <div className="flex-1" />
        {/* footer / profile */}
        <div className={`flex items-center gap-2 px-2 ${collapsed ? 'justify-center' : ''}`}>
          <div className="w-8 h-8 rounded-xl border border-indigo-200 bg-gradient-to-tr from-indigo-500 to-fuchsia-500" />
          <div className={`${collapsed ? 'hidden' : 'block'} text-xs text-gray-500`}>Kullanıcı</div>
        </div>
      </nav>
    </div>
  )

  return (
    <div className="min-h-screen grid grid-cols-12">
      {/* Mobile top bar */}
      <div className="col-span-12 md:hidden flex items-center justify-between p-3 sticky top-0 bg-white/90 backdrop-blur z-40 border-b">
        <button
          className="w-9 h-9 inline-flex items-center justify-center rounded-lg hover:bg-gray-100"
          onClick={() => setMobileOpen(true)}
          aria-label="Menüyü aç"
        >
          ☰
        </button>
        <div className="text-base font-semibold text-[var(--color-primary)]">CebimdekiVeri</div>
        <div className="w-9" />
      </div>

      {/* Desktop centered pill sidebar (fixed) */}
      <div className="hidden md:block col-span-12">
        <div className="fixed left-3 top-1/2 -translate-y-1/2 z-40">
          {SidebarContent}
        </div>
      </div>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div className="w-64 h-full bg-white shadow-2xl card glass border-r">
            <div className="h-full">{SidebarContent}</div>
          </div>
          <div className="flex-1 bg-black/30" onClick={() => setMobileOpen(false)} />
        </div>
      )}

      <main className="col-span-12 p-6 bg-[var(--color-background)] min-h-screen md:pl-24">
        <Outlet />
      </main>
    </div>
  )
}
