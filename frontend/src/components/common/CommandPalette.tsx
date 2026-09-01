import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Sparkles,
  Terminal,
  FlaskConical,
  AlertTriangle,
  Building2,
  Layers,
  FileText,
  RotateCcw,
  Zap,
  ArrowRight,
  Shield,
  HelpCircle,
  Calendar,
  Clock,
  BookOpen,
  GraduationCap,
  Users,
  CheckCircle2,
  Activity,
  Radio,
  Flame,
  User,
  Sliders,
  Palette,
  Eye,
  FileSearch,
  MessageSquareWarning,
  ListTodo,
  TrendingUp,
  Briefcase,
  Compass,
  Target,
} from 'lucide-react';
import { useAuth } from '../../auth/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { triggerSpotlight } from '../../utils/searchDeepLink';

export interface SearchCommandItem {
  id: string;
  label: string;
  category: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  tabKey?: string;
  targetId?: string;
  roles: Array<'student' | 'faculty' | 'management' | 'admin' | 'all'>;
  aliases: string[];
}

const SEARCH_DATABASE: SearchCommandItem[] = [
  // ==========================================
  // STUDENT SEARCH COMMANDS & DEEP-LINKS
  // ==========================================
  {
    id: 'student-attendance',
    label: 'Attendance & Attendance Trends',
    category: 'Academic Intelligence',
    description: 'View attendance percentages, subject breakdown, and AI trajectory',
    icon: Users,
    path: '/student/academics',
    tabKey: 'attendance',
    targetId: 'attendance',
    roles: ['student'],
    aliases: [
      'attendance', 'attend', 'present', 'absent', 'absence', 'absences',
      'bunk', 'percentage', 'records', 'classes', 'sessions', 'attendance trend',
      'overall attendance', 'shortage', '75 percent', 'roll call', 'condonation',
      'condonation range', 'detention', 'detention warning', 'viit attendance policy'
    ],
  },
  {
    id: 'student-assignments',
    label: 'Assignments & Deliverables',
    category: 'Academic Intelligence',
    description: 'Review pending assignments, due dates, and completion status',
    icon: ListTodo,
    path: '/student/academics',
    tabKey: 'assignments',
    targetId: 'assignments',
    roles: ['student'],
    aliases: [
      'assignment', 'assignments', 'homework', 'due', 'tasks', 'submissions',
      'deliverables', 'backlog', 'projects', 'deadlines', 'pending tasks',
      'coursework', 'submission date'
    ],
  },
  {
    id: 'student-assessments',
    label: 'Assessments & Examination Marks',
    category: 'Academic Intelligence',
    description: 'Track mid-term scores, continuous assessments, and academic performance',
    icon: GraduationCap,
    path: '/student/academics',
    tabKey: 'assessments',
    targetId: 'assessments',
    roles: ['student'],
    aliases: [
      'assessment', 'assessments', 'exams', 'marks', 'scores', 'tests',
      'quizzes', 'grades', 'internals', 'mid', 'midterm', 'mid exams',
      'semester', 'results', 'marks list', 'grade point', 'cie', 'see',
      'mid-1', 'mid-2', 'mid 1', 'mid 2', 'internal exam', 'lab internal', 'lab external'
    ],
  },
  {
    id: 'student-timetable',
    label: 'Weekly Timetable & Schedule',
    category: 'Academic Intelligence',
    description: 'View scheduled periods, classrooms, and lecture timings',
    icon: Clock,
    path: '/student/academics',
    tabKey: 'timetable',
    targetId: 'timetable',
    roles: ['student'],
    aliases: [
      'timetable', 'schedule', 'routine', 'classes', 'periods', 'slots',
      'rooms', 'lecture schedule', 'daily classes', 'timing', 'lecture timing'
    ],
  },
  {
    id: 'student-schedule-conflicts',
    label: 'Schedule Conflict Detection',
    category: 'Academic Intelligence',
    description: 'Deterministic detection of overlapping exam dates and time clashes',
    icon: AlertTriangle,
    path: '/student/academics',
    targetId: 'schedule-conflicts',
    roles: ['student'],
    aliases: [
      'conflict', 'conflicts', 'schedule conflict', 'exam overlap', 'clash',
      'time clash', 'overlap', 'exam clash', 'schedule warning'
    ],
  },
  {
    id: 'student-workload-concentration',
    label: 'Workload Concentration Alert',
    category: 'Academic Intelligence',
    description: 'Identifies multiple assignments due in close succession (3+ within 3 days)',
    icon: Flame,
    path: '/student/academics',
    targetId: 'workload-concentration',
    roles: ['student'],
    aliases: [
      'workload', 'workload concentration', 'stress', 'burden', 'busy',
      'deadline clustering', 'peak load', 'exam week', 'heavy workload', 'crunch'
    ],
  },
  {
    id: 'student-academic-insights',
    label: 'AI Academic Insights & Observations',
    category: 'Academic Intelligence',
    description: 'Data-grounded observations and personalized study suggestions',
    icon: Sparkles,
    path: '/student/academics',
    targetId: 'academic-insights',
    roles: ['student'],
    aliases: [
      'ai insights', 'academic insights', 'observations', 'recommendations',
      'academic warnings', 'predictions', 'study advice', 'suggestions'
    ],
  },
  {
    id: 'student-academic-calendar',
    label: 'Academic Calendar & Key Dates',
    category: 'Academic Intelligence',
    description: 'Campus schedule including instructional days, exam windows, and holidays',
    icon: Calendar,
    path: '/student/academics',
    tabKey: 'calendar',
    targetId: 'academic-calendar',
    roles: ['student'],
    aliases: [
      'calendar', 'academic calendar', 'events', 'holidays', 'fest',
      'important dates', 'vacation', 'exam calendar', 'semester start', 'end semester'
    ],
  },
  {
    id: 'student-enrolled-subjects',
    label: 'Enrolled Subjects & Faculty Contacts',
    category: 'Academic Intelligence',
    description: 'View registered courses, syllabus codes, and faculty instructors',
    icon: BookOpen,
    path: '/student/academics',
    tabKey: 'subjects',
    targetId: 'enrolled-subjects',
    roles: ['student'],
    aliases: [
      'subjects', 'courses', 'enrolled', 'curriculum', 'credits', 'syllabus',
      'faculty', 'professors', 'instructors', 'subject list', 'registered courses'
    ],
  },
  {
    id: 'student-career-overview',
    label: 'Career Intelligence & Recommended Opportunities',
    category: 'Career Intelligence',
    description: 'Explore personalized opportunity matches and verified skill requirements',
    icon: Briefcase,
    path: '/student/career',
    targetId: 'opportunities',
    roles: ['student'],
    aliases: [
      'career', 'job', 'jobs', 'internship', 'internships', 'opportunity', 'opportunities',
      'placement', 'placements', 'campus placement', 'placement cell', 'openings', 'vacancies',
      't&p', 't&p cell', 'crt', 'campus recruitment training', 'ai&ds', 'csm', 'csd', 'csc'
    ],
  },
  {
    id: 'student-career-strengths',
    label: 'Career Strengths & Domain Alignment',
    category: 'Career Intelligence',
    description: 'Explore academic-aware career strengths and domain fit scores',
    icon: Compass,
    path: '/student/career',
    targetId: 'strengths',
    roles: ['student'],
    aliases: [
      'career strengths', 'career fit', 'domain alignment', 'career direction',
      'strongest fields', 'what am i strong in', 'data science fit', 'ai/ml fit'
    ],
  },
  {
    id: 'student-career-resume',
    label: 'Resume & Verified Skills',
    category: 'Career Intelligence',
    description: 'Upload resume document, manage verified technical competencies and projects',
    icon: FileText,
    path: '/student/career',
    targetId: 'resume',
    roles: ['student'],
    aliases: [
      'resume', 'cv', 'skills', 'verified skills', 'upload resume', 'projects',
      'certifications', 'replace resume', 'technical skills'
    ],
  },
  {
    id: 'student-career-skill-gaps',
    label: 'Skill Gap Diagnostics',
    category: 'Career Intelligence',
    description: 'View identified skill gaps and recommended learning areas',
    icon: Sparkles,
    path: '/student/career',
    targetId: 'skill-gaps',
    roles: ['student'],
    aliases: [
      'skill gap', 'skill gaps', 'missing skills', 'learning recommendations',
      'what to learn', 'competencies', 'gap analysis'
    ],
  },
  {
    id: 'student-career-brief',
    label: 'Daily Career Brief & Closing Deadlines',
    category: 'Career Intelligence',
    description: 'Review daily matched opportunities and approaching deadlines',
    icon: Clock,
    path: '/student/career',
    targetId: 'brief',
    roles: ['student'],
    aliases: [
      'daily brief', 'career brief', 'closing soon', 'deadlines', 'internship deadlines',
      'approaching deadlines', 'career summary'
    ],
  },
  {
    id: 'student-report-issue',
    label: 'Report Campus Issue or Grievance',
    category: 'Grievances & Support',
    description: 'Submit maintenance defects, safety hazards, lab issues, or complaints',
    icon: MessageSquareWarning,
    path: '/student/report',
    targetId: 'report-issue',
    roles: ['student'],
    aliases: [
      'report', 'complaint', 'file complaint', 'grievance', 'ticket',
      'broken', 'issue', 'problem', 'defect', 'incident', 'report issue',
      'safety', 'infrastructure', 'wifi issue', 'hostel issue', 'lab issue'
    ],
  },
  {
    id: 'student-my-complaints',
    label: 'My Complaints & Grievance Tracking',
    category: 'Grievances & Support',
    description: 'Track the status and resolution timeline of submitted campus reports',
    icon: FileSearch,
    path: '/student/my-complaints',
    targetId: 'my-complaints',
    roles: ['student'],
    aliases: [
      'my complaints', 'my reports', 'my tickets', 'tracking', 'status',
      'complaint history', 'case status', 'grievance status', 'ticket status',
      'submitted issues', 'resolved issues'
    ],
  },
  {
    id: 'student-profile',
    label: 'Student Profile & Academic Record',
    category: 'Profile & Account',
    description: 'View registration number, department, year, and account details',
    icon: User,
    path: '/student/profile',
    targetId: 'student-profile',
    roles: ['student'],
    aliases: [
      'profile', 'student profile', 'my profile', 'account', 'roll number',
      'registration', 'year', 'branch', 'email', 'student id', 'personal info'
    ],
  },

  // ==========================================
  // FACULTY SEARCH COMMANDS & DEEP-LINKS
  // ==========================================
  {
    id: 'faculty-academic-overview',
    label: 'Faculty Academic Overview & Engagement',
    category: 'Academic Intelligence',
    description: 'Course attendance, assessment averages, and assignment submissions across batches',
    icon: GraduationCap,
    path: '/faculty/academic-intelligence',
    tabKey: 'overview',
    targetId: 'faculty-overview',
    roles: ['faculty'],
    aliases: [
      'faculty academics', 'teaching', 'classes', 'faculty overview',
      'course metrics', 'student engagement', 'course overview', 'teaching overview'
    ],
  },
  {
    id: 'faculty-attendance',
    label: 'Faculty Student Attendance Tracking',
    category: 'Academic Intelligence',
    description: 'Inspect class-by-class attendance, low-attendance alerts, and trends',
    icon: Users,
    path: '/faculty/academic-intelligence',
    tabKey: 'attendance',
    targetId: 'faculty-attendance',
    roles: ['faculty'],
    aliases: [
      'faculty attendance', 'mark attendance', 'student attendance',
      'absenteeism', 'lecture attendance', 'class attendance', 'attendance records'
    ],
  },
  {
    id: 'faculty-assignments',
    label: 'Faculty Assignment Velocity & Submissions',
    category: 'Academic Intelligence',
    description: 'Monitor submission velocity, pending homework, and completion rates',
    icon: ListTodo,
    path: '/faculty/academic-intelligence',
    tabKey: 'assignments',
    targetId: 'faculty-assignments',
    roles: ['faculty'],
    aliases: [
      'faculty assignments', 'grading', 'submissions', 'homework evaluation',
      'pending grading', 'assignment submissions', 'submission rates'
    ],
  },
  {
    id: 'faculty-assessments',
    label: 'Faculty Assessment & Gradebook Tracking',
    category: 'Academic Intelligence',
    description: 'Review mid-term distribution, internal marks, and exam averages',
    icon: BookOpen,
    path: '/faculty/academic-intelligence',
    tabKey: 'assessments',
    targetId: 'faculty-assessments',
    roles: ['faculty'],
    aliases: [
      'faculty assessments', 'gradebook', 'enter marks', 'mid marks',
      'internal assessment', 'marks distribution', 'exam results', 'grade sheet'
    ],
  },
  {
    id: 'faculty-timeline',
    label: 'Academic Timeline & Syllabus Pacing',
    category: 'Academic Intelligence',
    description: 'Curriculum delivery pacing, semester milestones, and exam periods',
    icon: Calendar,
    path: '/faculty/academic-intelligence',
    tabKey: 'timeline',
    targetId: 'faculty-timeline',
    roles: ['faculty'],
    aliases: [
      'academic timeline', 'syllabus pacing', 'semester progress',
      'lecture schedule', 'milestones', 'pacing', 'curriculum progress'
    ],
  },
  {
    id: 'faculty-related-cases',
    label: 'Related Academic Complaints & Cases',
    category: 'Academic Intelligence',
    description: 'Cross-reference student academic complaints linked to courses and labs',
    icon: MessageSquareWarning,
    path: '/faculty/academic-intelligence',
    tabKey: 'cases',
    targetId: 'faculty-related-cases',
    roles: ['faculty'],
    aliases: [
      'academic complaints', 'student concerns', 'course issues',
      'linked complaints', 'related cases', 'academic grievances'
    ],
  },
  {
    id: 'faculty-cases-queue',
    label: 'My Actionable Cases & Investigation Queue',
    category: 'Operations',
    description: 'Manage assigned student complaints, investigation notes, and resolution actions',
    icon: Shield,
    path: '/faculty/cases',
    targetId: 'faculty-cases-queue',
    roles: ['faculty'],
    aliases: [
      'cases', 'assigned cases', 'investigation', 'my cases',
      'complaint queue', 'resolution', 'investigation notes', 'actionable cases'
    ],
  },
  {
    id: 'faculty-feedback-overview',
    label: 'Feedback & Concern Intelligence',
    category: 'Feedback & Insights',
    description: 'Anonymized student feedback themes, sentiment clusters, and trend analysis',
    icon: Activity,
    path: '/faculty/feedback',
    targetId: 'faculty-feedback-overview',
    roles: ['faculty'],
    aliases: [
      'feedback', 'student feedback', 'concern themes', 'evaluations',
      'sentiment', 'anonymized concerns', 'feedback summary', 'concerns'
    ],
  },
  {
    id: 'faculty-department-issues',
    label: 'Department Workspace & Laboratory Issues',
    category: 'Department Operations',
    description: 'Departmental infrastructure, lab defect clusters, and classroom maintenance',
    icon: Building2,
    path: '/faculty/department-issues',
    targetId: 'department-issues',
    roles: ['faculty'],
    aliases: [
      'department issues', 'cse issues', 'lab issues', 'classroom defects',
      'equipment maintenance', 'dept complaints', 'lab maintenance', 'department workspace'
    ],
  },

  // ==========================================
  // MANAGEMENT / ADMIN COMMANDS & DEEP-LINKS
  // ==========================================
  {
    id: 'management-intelligence-center',
    label: 'Campus Command & AI Intelligence Center',
    category: 'Executive Intelligence',
    description: 'High-level operational overview, risk metrics, and campus intelligence score',
    icon: Sparkles,
    path: '/management',
    targetId: 'ai-intelligence-center',
    roles: ['management', 'admin'],
    aliases: [
      'management', 'intelligence center', 'command center', 'campus health',
      'overview', 'kpi', 'intelligence score', 'executive dashboard'
    ],
  },
  {
    id: 'management-metrics-overview',
    label: 'Top Operational Metrics & Case Counts',
    category: 'Executive Intelligence',
    description: 'Total central records, open cases, active clusters, and critical severity count',
    icon: Activity,
    path: '/management',
    targetId: 'management-overview',
    roles: ['management', 'admin'],
    aliases: [
      'total cases', 'open cases', 'high impact', 'kpi summary', 'metrics',
      'case counts', 'incident stats'
    ],
  },
  {
    id: 'management-domain-health-matrix',
    label: 'Campus Domain Health Matrix',
    category: 'Executive Intelligence',
    description: 'Deterministic operational health scoring across 7 campus functional domains',
    icon: Shield,
    path: '/management',
    targetId: 'domain-health-matrix',
    roles: ['management', 'admin'],
    aliases: [
      'domain health', 'health matrix', 'operations', 'transport health',
      'hostel health', 'academic health', 'infrastructure health', 'canteen health',
      '7 domains', 'domain status'
    ],
  },
  {
    id: 'management-intelligence-graph',
    label: 'Relational Intelligence Knowledge Graph',
    category: 'Executive Intelligence',
    description: 'Interactive graph connecting cases, physical locations, categories, and patterns',
    icon: Layers,
    path: '/management',
    targetId: 'intelligence-graph',
    roles: ['management', 'admin'],
    aliases: [
      'graph', 'relational graph', 'knowledge graph', 'complaint connections',
      'pattern clusters', 'network', 'spatial graph', 'interactive map'
    ],
  },
  {
    id: 'viit-campus-buildings',
    label: 'VIIT Campus Buildings & Locations',
    category: 'Campus Navigation',
    description: 'Explore campus infrastructure: APJ Abdul Kalam Block, Sir MV Block, Ramanujan Block, Vignan Dhara Library, Dharitri',
    icon: Building2,
    path: '/student/report',
    targetId: 'report-issue',
    roles: ['student', 'faculty', 'management', 'admin'],
    aliases: [
      'campus buildings', 'kalam block', 'apj block', 'sir mv block', 'visveswaraya block',
      'ramanujan block', 'aryabhata block', 'vignan dhara', 'central library', 'dharitri',
      'seminar hall', 'priyadarshini hostel', 'girls hostel', 'boys hostel', 'canteen'
    ],
  },
  {
    id: 'vignai-action-center',
    label: 'VIGNAI Action Center & Priorities',
    category: 'Action Intelligence',
    description: 'Review prioritized recommended actions and next steps across Academics, Career, and Operations',
    icon: Target,
    path: '/student/dashboard',
    targetId: 'vignai-action-center',
    roles: ['student', 'faculty', 'management', 'admin'],
    aliases: [
      'priorities', 'my priorities', 'action center', 'what should i focus on',
      'what should i do first', "today's priorities", 'actions', 'action intelligence',
      'next steps', 'to do', 'tasks'
    ],
  },
  {
    id: 'vignai-proactive-insights',
    label: 'VIGNAI Proactive Insights & Focus Areas',
    category: 'Cross-Domain Intelligence',
    description: 'Review multi-signal proactive insights across Academics, Career, and Operations',
    icon: Sparkles,
    path: '/student/dashboard',
    roles: ['student', 'faculty', 'management', 'admin'],
    aliases: [
      'insights', 'vignai insights', 'what should i focus on', 'career insights',
      'academic insights', 'campus insights', 'proactive insights', 'focus areas', 'recommendations'
    ],
  },
  {
    id: 'management-emerging-patterns',
    label: 'Emerging Pattern Clusters & Spatial Hotspots',
    category: 'Executive Intelligence',
    description: 'Autonomous spatial and temporal clustering over complaints and physical blocks',
    icon: Flame,
    path: '/management',
    targetId: 'emerging-patterns',
    roles: ['management', 'admin'],
    aliases: [
      'emerging patterns', 'clusters', 'hotspots', 'recurring issues',
      'spikes', 'trends', 'anomaly detection', 'spatial clusters', 'pattern detection'
    ],
  },
  {
    id: 'management-ai-priorities',
    label: 'AI Priority Queue & Risk Ranking',
    category: 'Executive Intelligence',
    description: 'Multi-signal algorithmic ranking prioritizing high-impact incidents',
    icon: Radio,
    path: '/management',
    targetId: 'ai-priorities',
    roles: ['management', 'admin'],
    aliases: [
      'ai priorities', 'priority queue', 'urgent issues', 'multi-signal ranking',
      'critical actions', 'prioritization', 'severity ranking'
    ],
  },
  {
    id: 'management-what-if-lab',
    label: 'What-If Lab — Decision Simulation Engine',
    category: 'Decision Modeling',
    description: 'Simulate transit additions, Wi-Fi upgrades, and technician staffing allocations',
    icon: FlaskConical,
    path: '/management/simulations',
    targetId: 'what-if-lab',
    roles: ['management', 'admin'],
    aliases: [
      'what if', 'simulations', 'what-if lab', 'simulation lab',
      'decision modeling', 'bus addition', 'wifi simulation', 'technician staffing',
      'resource planning', 'scenarios', 'trade-offs'
    ],
  },
  {
    id: 'management-opportunity-intake',
    label: 'Opportunity Intake & Source Management',
    category: 'Opportunity Management',
    description: 'Submit forwarded circulars, review opportunity drafts, and monitor connectors',
    icon: Briefcase,
    path: '/management/opportunity-intake',
    roles: ['management', 'faculty', 'admin'],
    aliases: [
      'opportunity intake', 'placement intake', 'intake', 'verify opportunities',
      'source health', 'sync sources', 'publish opportunity', 'placement coordinator'
    ],
  },
  {
    id: 'management-academic-overview',
    label: 'Institutional Academic Intelligence Overview',
    category: 'Institutional Intelligence',
    description: 'University-wide attendance, deliverable velocity, and departmental health',
    icon: GraduationCap,
    path: '/management/academics',
    targetId: 'management-academic-overview',
    roles: ['management', 'admin'],
    aliases: [
      'institutional academics', 'university academic overview', 'campus academic health',
      'global attendance', 'university performance', 'academic management'
    ],
  },
  {
    id: 'management-department-trends',
    label: 'Department Comparative Performance & Trends',
    category: 'Institutional Intelligence',
    description: 'Comparative engagement, attendance, and assignment velocity across departments',
    icon: TrendingUp,
    path: '/management/academics',
    targetId: 'department-trends',
    roles: ['management', 'admin'],
    aliases: [
      'department trends', 'department comparison', 'dept breakdown',
      'cross-department analytics', 'cse vs ece', 'department ranking'
    ],
  },
  {
    id: 'management-campus-issues',
    label: 'Campus Issues Registry & Case Filters',
    category: 'Operations',
    description: 'Browse, search, and filter centralized complaint records with status updates',
    icon: FileSearch,
    path: '/management/campus-issues',
    targetId: 'campus-issues',
    roles: ['management', 'admin'],
    aliases: [
      'campus issues', 'all complaints', 'central database', 'incident registry',
      'filter complaints', 'all tickets', 'issue search'
    ],
  },
  // ==========================================
  // UNIVERSAL SYSTEM COMMANDS (ALL ROLES)
  // ==========================================
  {
    id: 'universal-ask-vignai',
    label: 'Ask VIGNAI — Your AI Campus Assistant',
    category: 'AI Assistant',
    description: 'Query campus intelligence, academic records, and general knowledge in natural language',
    icon: Terminal,
    path: '/ask-vignai',
    targetId: 'ask-vignai-console',
    roles: ['all', 'student', 'faculty', 'management', 'admin'],
    aliases: [
      'ask vignai', 'ask vignai os', 'vignai', 'ask vignex', 'ask ai', 'ai query', 'natural language search',
      'campus qa', 'intelligence assistant', 'ai chat', 'vignai console', 'vignex console',
      'ai campus assistant', 'vignai assistant', 'campus assistant', 'assistant'
    ],
  },
  {
    id: 'universal-appearance-settings',
    label: 'Appearance Settings & OLED Theme',
    category: 'Preferences',
    description: 'Toggle True OLED Dark Mode, Midnight, Navy, or Classic Light themes',
    icon: Palette,
    path: '',
    targetId: 'appearance-settings',
    roles: ['all', 'student', 'faculty', 'management', 'admin'],
    aliases: [
      'appearance', 'theme', 'dark mode', 'light mode', 'oled', 'oled dark mode',
      'night mode', 'contrast', 'color theme', 'display settings', 'settings'
    ],
  },
];


export const CommandPalette: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();
  const { user } = useAuth();
  const { theme, setTheme } = useTheme();
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const userRole = (user?.role || 'student').toLowerCase() as 'student' | 'faculty' | 'management' | 'admin';

  // Keyboard shortcut listener (Ctrl+K or Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setSelectedIndex(0);
    } else {
      setSearch('');
    }
  }, [isOpen]);

  // Role-Filtered Search Index with Fuzzy Multi-Token Matcher
  const filteredCommands = useMemo(() => {
    const roleFiltered = SEARCH_DATABASE.filter((cmd) => {
      if (cmd.roles.includes('all')) return true;
      if (userRole === 'admin') return cmd.roles.includes('management') || cmd.roles.includes('admin');
      return cmd.roles.includes(userRole);
    });

    const query = search.trim().toLowerCase();
    if (!query) return roleFiltered;

    const queryTokens = query.split(/\s+/).filter(Boolean);

    return roleFiltered
      .map((cmd) => {
        const labelLower = cmd.label.toLowerCase();
        const descLower = cmd.description.toLowerCase();
        const catLower = cmd.category.toLowerCase();
        const aliasesStr = cmd.aliases.join(' ').toLowerCase();
        const searchableText = `${labelLower} ${descLower} ${catLower} ${aliasesStr}`;

        // Every query token must match somewhere
        const matchesAllTokens = queryTokens.every((token) => searchableText.includes(token));
        if (!matchesAllTokens) return null;

        // Calculate relevance score
        let score = 0;
        if (labelLower === query) score += 100;
        else if (labelLower.startsWith(query)) score += 60;
        else if (labelLower.includes(query)) score += 40;

        if (cmd.aliases.some((a) => a === query)) score += 80;
        else if (cmd.aliases.some((a) => a.startsWith(query))) score += 50;
        else if (cmd.aliases.some((a) => a.includes(query))) score += 30;

        if (catLower.includes(query)) score += 20;
        if (descLower.includes(query)) score += 10;

        return { item: cmd, score };
      })
      .filter((res): res is { item: SearchCommandItem; score: number } => res !== null)
      .sort((a, b) => b.score - a.score)
      .map((res) => res.item);
  }, [userRole, search]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [filteredCommands]);

  const handleSelect = (item: SearchCommandItem) => {
    setIsOpen(false);

    // Appearance action special case
    if (item.targetId === 'appearance-settings' && !item.path) {
      triggerSpotlight('appearance-settings', 3500);
      return;
    }

    // Ask VIGNAI role-based navigation
    if (item.id === 'universal-ask-vignai' || item.id === 'universal-ask-vignex') {
      navigate(`/${userRole}/ask-vignai`, {
        state: {
          targetId: 'ask-vignai-console',
        },
      });
      triggerSpotlight('ask-vignai-console', 3500);
      return;
    }

    // Standard Deep-Link Navigation
    if (item.path) {
      navigate(item.path + (item.targetId ? `#${item.targetId}` : ''), {
        state: {
          targetId: item.targetId,
          activeTab: item.tabKey,
        },
      });

      if (item.targetId) {
        triggerSpotlight(item.targetId, 3500);
      }
    }
  };

  const handleKeyDownInput = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < filteredCommands.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : filteredCommands.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredCommands[selectedIndex]) {
        handleSelect(filteredCommands[selectedIndex]);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-24 bg-black/70 dark:bg-black/85 backdrop-blur-md p-4 animate-fade-in">
      <div className="bg-white dark:bg-[#050505] rounded-3xl shadow-2xl border border-slate-200 dark:border-white/10 max-w-2xl w-full overflow-hidden flex flex-col max-h-[80vh]">
        {/* Search Header */}
        <div className="relative flex items-center px-4 pt-3.5 pb-3 border-b border-slate-100 dark:border-white/10">
          <Search className="h-5 w-5 text-slate-400 dark:text-zinc-500 mr-2.5 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={handleKeyDownInput}
            placeholder={`Search ${userRole.toUpperCase()} functions, academic sections, complaints, themes (Ctrl+K)...`}
            className="w-full text-sm sm:text-base bg-transparent text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none"
          />
          <div className="flex items-center gap-1.5 shrink-0 ml-2">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded">
              {userRole}
            </span>
            <span className="text-[10px] font-mono font-bold text-slate-400 dark:text-zinc-500 bg-slate-100 dark:bg-[#161616] px-2 py-0.5 rounded">
              ESC
            </span>
          </div>
        </div>

        {/* Command List */}
        <div ref={listRef} className="overflow-y-auto p-2 space-y-1 flex-1">
          {filteredCommands.length === 0 ? (
            <div className="text-center py-10 space-y-2">
              <p className="text-sm font-medium text-slate-500 dark:text-zinc-400">
                No matching functions or sections found for "{search}".
              </p>
              <p className="text-xs text-slate-400 dark:text-zinc-500">
                Try searching for attendance, assignments, timetable, workload, exams, complaints, or appearance.
              </p>
            </div>
          ) : (
            filteredCommands.map((cmd, idx) => {
              const Icon = cmd.icon;
              const isSelected = idx === selectedIndex;
              return (
                <button
                  key={cmd.id}
                  onClick={() => handleSelect(cmd)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`w-full flex items-center justify-between p-3 rounded-2xl text-left transition-all group ${
                    isSelected
                      ? 'bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/50'
                      : 'hover:bg-slate-50 dark:hover:bg-[#0A0A0A] border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3.5 min-w-0">
                    <div
                      className={`flex h-10 w-10 items-center justify-center rounded-xl transition-colors shrink-0 ${
                        isSelected
                          ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                          : 'bg-slate-100 dark:bg-[#101010] text-slate-700 dark:text-zinc-300 group-hover:bg-slate-200 dark:group-hover:bg-[#181818]'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span
                          className={`text-sm font-bold transition-colors ${
                            isSelected
                              ? 'text-indigo-600 dark:text-indigo-300'
                              : 'text-slate-900 dark:text-white'
                          }`}
                        >
                          {cmd.label}
                        </span>
                        <span className="text-[9px] font-semibold text-slate-400 dark:text-zinc-500 bg-slate-100 dark:bg-[#161616] px-1.5 py-0.2 rounded">
                          {cmd.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 dark:text-zinc-400 truncate mt-0.5">
                        {cmd.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0 ml-2">
                    {cmd.targetId && (
                      <span className="text-[10px] font-mono text-slate-400 dark:text-zinc-500 hidden sm:inline-block">
                        #{cmd.targetId}
                      </span>
                    )}
                    <ArrowRight
                      className={`h-4 w-4 transition-transform ${
                        isSelected
                          ? 'text-indigo-600 dark:text-indigo-400 translate-x-0.5'
                          : 'text-slate-300 dark:text-zinc-600'
                      }`}
                    />
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-[#0A0A0A] border-t border-slate-100 dark:border-white/10 text-[11px] text-slate-400 dark:text-zinc-500">
          <div className="flex items-center gap-1.5">
            <Sparkles className="h-3.5 w-3.5 text-indigo-500" />
            <span>VIGNAI OS Deep-Link Function Finder & Spotlight</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline">↑↓ Navigate</span>
            <span className="hidden sm:inline">↵ Select & Spotlight</span>
            <span>ESC Close</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommandPalette;

