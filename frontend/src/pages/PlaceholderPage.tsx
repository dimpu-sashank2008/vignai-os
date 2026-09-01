import React from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../auth/AuthContext';
import { Role } from '../types';

interface PlaceholderPageProps {
  title: string;
  description?: string;
  badgeText?: string;
}

const roleBadgeVariant: Record<Role, 'info' | 'warning' | 'danger'> = {
  student: 'info',
  faculty: 'warning',
  management: 'danger',
};

export const PlaceholderPage: React.FC<PlaceholderPageProps> = ({
  title,
  description = 'This module will be fully implemented in upcoming phases.',
  badgeText,
}) => {
  const { user } = useAuth();
  const role = user?.role || 'student';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
        <p className="text-slate-600 mt-1">Logged in as {user?.email}</p>
      </div>

      <Card padding="lg">
        <div className="text-center py-12">
          <Badge variant={roleBadgeVariant[role]} className="mb-4">
            {badgeText || `${role.toUpperCase()} Module`}
          </Badge>
          <h2 className="text-xl font-semibold text-slate-900 mb-2">{title}</h2>
          <p className="text-slate-500 max-w-md mx-auto">{description}</p>
        </div>
      </Card>
    </div>
  );
};

export default PlaceholderPage;
