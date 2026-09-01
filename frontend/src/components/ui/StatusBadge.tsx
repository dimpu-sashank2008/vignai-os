import React from 'react';
import { Badge } from './Badge';

export type StatusType = 'active' | 'inactive' | 'pending' | 'resolved' | 'in_progress';

interface StatusBadgeProps {
  status: StatusType;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const config: Record<StatusType, { variant: 'default' | 'success' | 'warning' | 'danger' | 'info'; label: string }> = {
    active: { variant: 'success', label: 'Active' },
    inactive: { variant: 'danger', label: 'Inactive' },
    pending: { variant: 'warning', label: 'Pending' },
    resolved: { variant: 'info', label: 'Resolved' },
    in_progress: { variant: 'default', label: 'In Progress' },
  };

  const { variant, label } = config[status];

  return (
    <Badge variant={variant} className={className}>
      {label}
    </Badge>
  );
};
