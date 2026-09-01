import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { useToast } from './Toast';

interface CopyButtonProps {
  text: string;
  label?: string;
  className?: string;
  iconOnly?: boolean;
  toastMessage?: string;
}

export const CopyButton: React.FC<CopyButtonProps> = ({
  text,
  label = 'Copy',
  className = '',
  iconOnly = false,
  toastMessage = 'Copied to clipboard',
}) => {
  const [copied, setCopied] = useState(false);
  let toastContext: any;
  try {
    toastContext = useToast();
  } catch {
    // Fallback if rendered outside ToastProvider
  }

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback for non-https or older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }

      setCopied(true);
      if (toastContext?.success) {
        toastContext.success(toastMessage);
      }
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  return (
    <button
      type="button"
      onClick={handleCopy}
      aria-label={copied ? 'Copied' : `Copy ${text}`}
      title={copied ? 'Copied!' : `Copy ${text}`}
      className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-semibold transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 active:scale-95 ${
        copied
          ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/40'
          : 'bg-slate-100 hover:bg-slate-200 dark:bg-[#101010] dark:hover:bg-[#181818] text-slate-600 dark:text-zinc-300 border border-slate-200 dark:border-white/10'
      } ${className}`}
    >
      {copied ? (
        <>
          <Check className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
          {!iconOnly && <span>Copied</span>}
        </>
      ) : (
        <>
          <Copy className="h-3.5 w-3.5 shrink-0" />
          {!iconOnly && <span>{label}</span>}
        </>
      )}
    </button>
  );
};
