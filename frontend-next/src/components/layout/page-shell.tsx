import Link from 'next/link';

export function PageShell({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold">{title}</h1>
          {description ? <p className="text-sm text-muted">{description}</p> : null}
        </header>
        <nav className="flex flex-wrap gap-2 text-xs">
          {[
            ['/dashboard/admin', 'Dashboard Admin'],
            ['/dashboard/user', 'Dashboard User'],
            ['/tenants', 'Tenants'],
            ['/users', 'Users'],
            ['/leads', 'Leads'],
            ['/campaigns', 'Campaigns'],
            ['/whatsapp/instances', 'WhatsApp'],
            ['/documents', 'Documents'],
            ['/calendar', 'Calendar'],
            ['/agent', 'Agent'],
            ['/automations', 'Automations'],
            ['/settings/profile', 'Settings'],
            ['/health', 'Health'],
          ].map(([href, label]) => (
            <Link key={href} href={href} className="rounded border border-border px-2 py-1 hover:border-primary">
              {label}
            </Link>
          ))}
        </nav>
        {children}
      </div>
    </div>
  );
}
