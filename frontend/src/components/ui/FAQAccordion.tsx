import React, { useState } from 'react';
import { ChevronDown, HelpCircle, ShieldCheck, Sparkles, Lock, Cpu } from 'lucide-react';

export interface FAQItem {
  id: string;
  question: string;
  answer: string;
  category?: string;
  icon?: React.ElementType;
}

interface FAQAccordionProps {
  items?: FAQItem[];
  className?: string;
  title?: string;
}

export const DEFAULT_VIGNAI_FAQS: FAQItem[] = [
  {
    id: 'what-is-vignai',
    question: 'What is VIGNAI OS?',
    answer: 'VIGNAI OS is Vignan\'s AI-native Campus Operating System. It connects Academic Intelligence, Career Fit, Proactive Institutional Alerts, and Decision Support into a single privacy-preserving platform for Students, Faculty, and Management.',
    icon: Sparkles,
  },
  {
    id: 'privacy-protection',
    question: 'How is student and faculty privacy protected?',
    answer: 'VIGNAI OS enforces strict Role-Based Access Control (RBAC) at the server boundary. Sensitive student grievances are cryptographically anonymized, faculty cannot inspect private career profiles, and management views institutional aggregates without exposed student identities.',
    icon: Lock,
  },
  {
    id: 'career-fit-math',
    question: 'How does the Personalized Career Fit score work?',
    answer: 'Career Fit uses a deterministic, transparent formula: 45% Skill Match + 25% Domain Alignment + 15% Academic Performance + 15% Declared Interests. Ineligible opportunities are automatically penalized and cannot rank in top spots.',
    icon: Cpu,
  },
  {
    id: 'decision-support',
    question: 'Can VIGNAI make autonomous disciplinary or hiring decisions?',
    answer: 'No. VIGNAI is strictly a Decision Support System. It provides transparent mathematical rankings and evidence breakdowns ([Why first?]), but never autonomously grades, hires, disciplines students, or ranks teachers.',
    icon: ShieldCheck,
  },
  {
    id: 'viit-regulations',
    question: 'Does VIGNAI understand VIIT academic regulations (VR22/VR20)?',
    answer: 'Yes. VIGNAI includes a centralized VIIT Context Layer with official syllabus codes, 75% attendance condonation thresholds (65%-75% medical), CIE/SEE evaluation rules, and campus building mappings (Kalam Block, Sir MV Block, Vignan Dhara).',
    icon: HelpCircle,
  },
];

export const FAQAccordion: React.FC<FAQAccordionProps> = ({
  items = DEFAULT_VIGNAI_FAQS,
  className = '',
  title = 'Frequently Asked Questions & System Guide',
}) => {
  const [openIds, setOpenIds] = useState<Set<string>>(new Set([items[0]?.id || '']));

  const toggleItem = (id: string) => {
    setOpenIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {title && (
        <div className="flex items-center gap-2">
          <HelpCircle className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
          <h3 className="text-sm font-bold text-slate-800 dark:text-zinc-200 uppercase tracking-wider">
            {title}
          </h3>
        </div>
      )}

      <div className="space-y-2.5">
        {items.map((item) => {
          const isOpen = openIds.has(item.id);
          const Icon = item.icon || HelpCircle;

          return (
            <div
              key={item.id}
              className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#050505] overflow-hidden transition-colors shadow-sm"
            >
              <button
                type="button"
                onClick={() => toggleItem(item.id)}
                aria-expanded={isOpen}
                aria-controls={`faq-answer-${item.id}`}
                className="w-full flex items-center justify-between p-4 text-left gap-3 hover:bg-slate-50 dark:hover:bg-[#0A0A0A] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 shrink-0">
                    <Icon className="h-4 w-4" />
                  </div>
                  <span className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                    {item.question}
                  </span>
                </div>
                <ChevronDown
                  className={`h-4 w-4 text-slate-400 dark:text-zinc-500 transition-transform duration-200 shrink-0 ${
                    isOpen ? 'rotate-180 text-indigo-600 dark:text-indigo-400' : ''
                  }`}
                />
              </button>

              {isOpen && (
                <div
                  id={`faq-answer-${item.id}`}
                  className="px-4 pb-4 pt-1 text-xs sm:text-sm text-slate-600 dark:text-zinc-300 leading-relaxed border-t border-slate-100 dark:border-white/5 bg-slate-50/50 dark:bg-[#080808]"
                >
                  {item.answer}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
