import * as React from 'react';
import { cn } from '@/lib';

export function Button({ className, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className={cn('bg-primary text-primary-foreground px-3 py-2 text-sm', className)} {...props} />;
}
