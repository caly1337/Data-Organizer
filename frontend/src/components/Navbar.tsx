'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path || pathname.startsWith(path + '/');
  };

  return (
    <nav className="border-b bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-8 py-4">
        <div className="flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold hover:text-blue-600 transition-colors">
            Data-Organizer
          </Link>

          <div className="flex gap-6">
            <Link
              href="/scans"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/scans')
                  ? 'bg-blue-600 text-white'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              Scans
            </Link>

            <Link
              href="/providers"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/providers')
                  ? 'bg-blue-600 text-white'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              Providers
            </Link>

            <Link
              href="/settings"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/settings')
                  ? 'bg-blue-600 text-white'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              ⚙️ Settings
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
