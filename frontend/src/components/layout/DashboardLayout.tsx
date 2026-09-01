import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { CommandPalette } from '../common/CommandPalette';
import { VignaiWelcomeNotification } from '../common/VignaiWelcomeNotification';
import { BackToTopButton } from '../ui/BackToTopButton';

export const DashboardLayout: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-black text-slate-900 dark:text-zinc-100 transition-colors">
      {/* Accessible Skip to Main Content Link (First Keyboard Focusable Element) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-indigo-600 focus:text-white focus:text-xs focus:font-bold focus:rounded-xl focus:shadow-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-indigo-500"
      >
        Skip to main content
      </a>

      <CommandPalette />
      <VignaiWelcomeNotification />
      <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />
      
      <div className="flex flex-col lg:pl-64 min-h-screen">
        <TopNav onToggleSidebar={toggleSidebar} />
        
        <main id="main-content" tabIndex={-1} className="flex-1 p-4 sm:p-6 lg:p-8 focus:outline-none">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>

      <BackToTopButton />
    </div>
  );
};

