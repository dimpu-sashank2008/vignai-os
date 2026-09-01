export type Role = 'student' | 'faculty' | 'management';

export type CaseStatus = 'SUBMITTED' | 'UNDER_REVIEW' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
export type CasePriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AIProcessingStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
export type SensitivityLevel = 'NORMAL' | 'SENSITIVE' | 'HIGH_SENSITIVITY';
export type RouteType = 'DEPARTMENT_AND_MANAGEMENT' | 'MANAGEMENT_ONLY' | 'AUTHORIZED_GRIEVANCE' | 'CAMPUS_OPERATIONS' | 'OTHER';

export interface StudentProfile {
  id: number;
  enrollment_number?: string;
  year_of_study?: number;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  role: Role;
  is_active: boolean;
  roll_number?: string;
  faculty_id?: string;
  management_id?: string;
  must_change_password?: boolean;
  created_at: string;
  student_profile?: StudentProfile;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface LoginCredentials {
  identifier?: string;
  email?: string;
  password: string;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface ChangePasswordResponse {
  message: string;
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Evidence {
  id: number;
  complaint_id: number;
  file_name: string;
  file_type: string;
  file_size: number;
  created_at: string;
}

export interface ComplaintAIAnalysis {
  id: number;
  complaint_id: number;
  category?: string;
  subcategory?: string;
  issue_summary?: string;
  location?: string;
  duration?: string;
  impact?: string;
  suggested_priority?: CasePriority;
  priority_reason?: string;
  confidence?: number;
  processing_status: AIProcessingStatus;
  provider: string;
  model?: string;
  error_message?: string;

  // Phase 3 Routing Analysis
  department?: string;
  suggested_route_type?: RouteType;
  sensitivity?: SensitivityLevel;
  routing_reason?: string;

  created_at: string;
  updated_at: string;
}

export interface RoutingAudit {
  id: number;
  complaint_id: number;
  ai_suggested_route: string;
  policy_validation_result: string;
  final_route: string;
  decision_by: string;
  decision_reason: string;
  created_at: string;
}

export interface InvestigationNote {
  id: number;
  complaint_id: number;
  author_user_id: number;
  author_role: string;
  author_email: string;
  note_type: 'INTERNAL' | 'ACTION' | 'INVESTIGATION' | 'ESCALATION' | 'STUDENT_QUERY';
  content: string;
  is_visible_to_student: boolean;
  created_at: string;
}

export interface RelatedCase {
  case_id: string;
  title?: string;
  category?: string;
  location?: string;
  status: string;
  similarity_score: number;
  reason: string;
}

export interface Complaint {
  id: number;
  case_id: string;
  student_id: number;
  title?: string;
  description: string;
  location?: string;
  category?: string;
  status: CaseStatus;
  priority: CasePriority;
  identity_protected: boolean;
  created_at: string;
  updated_at: string;
  evidences: Evidence[];
  ai_analysis?: ComplaintAIAnalysis;
}

export interface ReporterInfo {
  is_protected: boolean;
  visibility: string;
  email?: string | null;
  enrollment_number?: string | null;
  year_of_study?: number | null;
}

export interface ManagementComplaint {
  id: number;
  case_id: string;
  title?: string;
  description: string;
  location?: string;
  category?: string;
  status: CaseStatus;
  priority: CasePriority;
  identity_protected: boolean;
  reporter_visibility: string;
  reporter_email?: string | null;
  evidence_count: number;
  ai_analysis?: ComplaintAIAnalysis;
  created_at: string;
  updated_at: string;
}

export interface ManagementComplaintDetail extends ManagementComplaint {
  reporter: ReporterInfo;
  evidences: Evidence[];
  routing_audit?: RoutingAudit;
  investigation_notes?: InvestigationNote[];
}

export interface ManagementSummary {
  total: number;
  open: number;
  under_review: number;
  in_progress: number;
  resolved: number;
  closed: number;
}

export interface FacultySummary {
  total_assigned: number;
  pending_review: number;
  in_progress: number;
  resolved: number;
  high_priority: number;
}

export interface ComplaintSummary {
  total: number;
  open: number;
  under_review: number;
  in_progress: number;
  resolved: number;
  closed: number;
}

// Phase 4A Intelligence Interfaces
export interface EmergingPattern {
  id: number;
  title: string;
  description: string;
  pattern_type: 'LOCATION_CLUSTER' | 'CATEGORY_BURST' | 'RECURRING_DEFECT' | 'CROSS_DEPT_RISK';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  case_count: number;
  affected_estimate: string;
  trend: 'RISING' | 'STABLE' | 'RESOLVING';
  evidence_case_ids: string[];
  confidence: number;
  primary_department?: string | null;
  primary_location?: string | null;
  status: string;
  created_at: string;
}

export interface CampusIntelligenceSummary {
  total_cases: number;
  open_cases_count?: number;
  emerging_patterns_count: number;
  high_impact_risks: number;
  recommended_actions_count: number;
  campus_intelligence_score: number;
  score_status: 'OPTIMAL' | 'GOOD' | 'MODERATE' | 'CRITICAL';
  score_breakdown: Record<string, any>;
  is_sufficient_data: boolean;
}

export interface AIPriorityItem {
  case_id: string;
  title: string;
  category?: string | null;
  location?: string | null;
  department?: string | null;
  ai_suggested_priority: string;
  current_status: string;
  calculated_score: number;
  score_factors: string[];
  created_at: string;
}

export interface DomainHealthItem {
  domain: string;
  health_status: 'Healthy' | 'Watch' | 'Elevated' | 'High Risk';
  active_cases: number;
  critical_cases: number;
  patterns_count: number;
  trend: string;
  primary_issue_summary: string;
  supporting_case_ids: string[];
}

export interface CampusTrendAnalytics {
  volume_timeline: Array<{ date: string; volume: number }>;
  category_distribution: Array<{ category: string; count: number }>;
  department_distribution: Array<{ department: string; count: number }>;
  status_distribution: Array<{ status: string; count: number }>;
  priority_distribution: Array<{ priority: string; count: number }>;
  resolution_rate: number;
  time_range: string;
}

export interface AIActivityEvent {
  id: string;
  event_type: 'ANALYSIS' | 'ROUTING' | 'PATTERN_DISCOVERY' | 'ACTION_LOG' | 'ESCALATION';
  case_id?: string | null;
  title: string;
  description: string;
  timestamp: string;
  tag: string;
}

export interface ComplaintCreateData {
  description: string;
  location?: string;
  category?: string;
  identity_protected: boolean;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'CASE' | 'LOCATION' | 'CATEGORY' | 'DEPARTMENT' | 'PATTERN';
  data: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  type: string;
}

export interface IntelligenceGraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metrics: {
    total_nodes: number;
    total_edges: number;
    cases_count: number;
    patterns_count: number;
    locations_count: number;
    categories_count: number;
    departments_count: number;
  };
}

export interface WhyInsightSignal {
  name: string;
  weight: string;
  evidence: string;
}

export interface WhyInsightResponse {
  insight_id: string;
  insight_type: string;
  title: string;
  supporting_case_count: number;
  supporting_case_ids: string[];
  locations: string[];
  categories: string[];
  departments: string[];
  data_window: string;
  signals: WhyInsightSignal[];
  interpretation: string;
  limitations: string;
}

export interface AskVignexEvidenceCase {
  case_id: string;
  title: string;
  category?: string | null;
  location?: string | null;
  priority: string;
  status: string;
}

export type QueryMode = 'GENERAL_KNOWLEDGE' | 'VIGNEX_DATA' | 'HYBRID';

export interface GroupExplainabilitySignal {
  name: string;
  weight: string;
  evidence: string;
}

export interface GroupUnderlyingCase {
  id: number;
  case_id: string;
  title?: string | null;
  description: string;
  location?: string | null;
  category?: string | null;
  status: CaseStatus;
  priority: CasePriority;
  identity_protected: boolean;
  reporter_visibility: string;
  reporter_email?: string | null;
  evidence_count: number;
  department?: string | null;
  created_at: string;
  updated_at: string;
}

export interface RelatedCaseGroup {
  id: string;
  group_key: string;
  title: string;
  description: string;
  category: string;
  location?: string | null;
  department?: string | null;
  priority: CasePriority;
  case_count: number;
  trend: 'Increasing' | 'Stable' | 'Resolving' | string;
  status: CaseStatus;
  primary_case_id: string;
  supporting_case_ids: string[];
  explainability_signals: GroupExplainabilitySignal[];
  grouping_label: string;
  ai_assisted_priority: boolean;
  priority_reason?: string;
  created_at: string;
  updated_at: string;
  cases?: GroupUnderlyingCase[];
}

export interface AskVignexActionLink {
  label: string;
  url: string;
  action_type: string;
}

export interface AskVignexAnswerResponse {
  query: string;
  intent: string;
  query_mode?: QueryMode;
  domain?: string;
  context_badge?: string;
  answer: string;
  key_findings: string[];
  supporting_case_ids: string[];
  supporting_cases: Array<{
    case_id: string;
    title: string;
    category?: string | null;
    location?: string | null;
    priority: string;
    status: string;
  }>;
  data_window: string;
  provenance: Record<string, any>;
  interpretation: string;
  limitations: string[];
  action_links: AskVignexActionLink[];
  ai_assisted: boolean;
  provider?: string;
  model?: string;
  provider_status?: string;
  tools_called?: string[];
  latency_ms?: number | null;
  created_at: string;
}

export interface AskVignexResponse extends AskVignexAnswerResponse {}

export interface SimulationScenarioConfig {
  scenario_id: string;
  name: string;
  parameters: Record<string, any>;
}

export interface SimulationMetricResult {
  name: string;
  baseline_value: number;
  scenario_value: number;
  difference: number;
  percentage_change?: number;
  unit: string;
  trend_direction: 'BETTER' | 'WORSE' | 'NEUTRAL';
}

export interface SimulationScenarioResult {
  scenario_id: string;
  name: string;
  metrics: SimulationMetricResult[];
  estimated_complaint_reduction_pct: number;
  estimated_cost_monthly: string;
  estimated_affected_users: string;
  operational_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  assumptions: string[];
  ai_scenario_explanation: string;
  data_source_label?: string;
}

export interface AIExplanationResponse {
  summary: string;
  benefits: string[];
  tradeoffs: string[];
  risks: string[];
  assumptions: string[];
  limitations: string[];
  recommended_action: string;
  human_authority_notice: string;
}

export interface SimulationComparisonResponse {
  domain: string;
  scenario_name: string;
  baseline_overview: Record<string, any>;
  scenarios: SimulationScenarioResult[];
  ai_explanation: AIExplanationResponse;
  data_sources: string[];
  assumptions_summary: string[];
  limitations_summary: string[];
  is_synthetic_model: boolean;
  model_notice: string;
}

export interface SavedSimulationResponse {
  id: number;
  user_id: number | null;
  name: string;
  scenario_type: string;
  input_data: Record<string, any>;
  result_data: Record<string, any>;
  created_at: string;
}

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  is_read: boolean;
  notification_type?: string;
  target_route?: string | null;
  target_entity_type?: string | null;
  target_entity_id?: string | null;
  target_anchor?: string | null;
  target_query?: string | null;
  source_action_id?: number | null;
  source_insight_id?: number | null;
  source_alert_id?: number | null;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────
// Phase 6 Academic Intelligence Interfaces
// ─────────────────────────────────────────────────────────────

export interface StudentAcademicOverview {
  data_source: string;
  metric_type: string;
  enrolled_subjects: number;
  overall_attendance_pct: number;
  attendance_present: number;
  attendance_total: number;
  assessment_average_pct: number;
  pending_assignments: number;
  upcoming_assessments_7d: number;
  workload_next_3d: number;
  workload_next_7d: number;
  workload_concentration_detected: boolean;
}

export interface StudentAcademicSubject {
  subject_id: number;
  code: string;
  name: string;
  credits: number;
  semester: number;
  section: string;
  data_source: string;
  attendance: {
    percentage: number;
    present: number;
    total: number;
  };
  last_assessment_score: number | null;
  last_assessment_score_pct: number | null;
  pending_assignments: number;
  next_assessment: {
    id: number;
    title: string;
    type: string;
    scheduled_at: string | null;
  } | null;
}

export interface AttendanceRecordLog {
  date: string;
  status: 'PRESENT' | 'ABSENT' | 'OD' | 'OTHER' | string;
}

export interface AttendanceTrendInfo {
  direction: 'IMPROVING' | 'DECLINING' | string;
  from_pct: number;
  to_pct: number;
  change_pp: number;
  data_basis: string;
}

export interface SubjectAttendanceDetail {
  subject_id: number;
  code: string;
  name: string;
  metric_type: string;
  data_source: string;
  percentage: number;
  present: number;
  absent: number;
  od: number;
  total: number;
  trend: AttendanceTrendInfo | null;
  recent_records: AttendanceRecordLog[];
}

export interface StudentAcademicAttendance {
  data_source: string;
  metric_type: string;
  overall: {
    total: number;
    present: number;
    absent: number;
    od: number;
    percentage: number;
  };
  subjects: SubjectAttendanceDetail[];
}

export interface CompletedAssessmentItem {
  assessment_id: number;
  title: string;
  type: string;
  subject: string;
  subject_code: string;
  scheduled_at: string | null;
  marks: number;
  max_marks: number;
  percentage: number;
  metric_type: string;
  data_source: string;
}

export interface UpcomingAssessmentItem {
  assessment_id: number;
  title: string;
  type: string;
  subject: string;
  subject_code: string;
  scheduled_at: string | null;
  max_marks: number;
  data_source: string;
}

export interface StudentAcademicAssessments {
  data_source: string;
  metric_type: string;
  overall_average_pct: number;
  completed: CompletedAssessmentItem[];
  upcoming: UpcomingAssessmentItem[];
}

export interface AcademicAssignmentItem {
  id: number;
  title: string;
  subject: string;
  subject_code: string;
  due_at: string | null;
  status: 'PENDING' | 'SUBMITTED' | 'COMPLETED' | 'OVERDUE' | string;
  submitted_at: string | null;
  data_source: string;
}

export interface StudentAcademicAssignments {
  data_source: string;
  metric_type: string;
  counts: {
    pending: number;
    overdue: number;
    submitted: number;
    completed: number;
    total: number;
  };
  pending: AcademicAssignmentItem[];
  overdue: AcademicAssignmentItem[];
  submitted: AcademicAssignmentItem[];
  completed: AcademicAssignmentItem[];
}

export interface TimetableSlot {
  entry_id: number;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  start_time: string;
  end_time: string;
  room?: string | null;
}

export interface TimetableConflict {
  type: string;
  day: string;
  entry_a: string;
  entry_b: string;
}

export interface StudentAcademicTimetable {
  data_source: string;
  by_day: Record<string, TimetableSlot[]>;
  conflicts_detected: boolean;
  conflicts: TimetableConflict[];
}

export interface WorkloadEventItem {
  type: string;
  title: string;
  date: string | null;
  subject_id: number;
}

export interface StudentAcademicWorkload {
  data_source: string;
  metric_type: string;
  today: string;
  next_3_days: {
    start: string;
    end: string;
    total_events: number;
    events: WorkloadEventItem[];
  };
  next_7_days: {
    start: string;
    end: string;
    total_events: number;
    events: WorkloadEventItem[];
  };
  concentration_detected: boolean;
  concentration_dates: string[];
}

export interface AcademicAIInsight {
  insight_type: string;
  title: string;
  summary: string;
  supporting_factors: string[];
  limitations: string[];
  recommended_action?: string | null;
  confidence: number;
  data_source: string;
  metric_type: string;
}

export interface FacultySubjectSummary {
  subject_id: number;
  code: string;
  name: string;
  data_source: string;
  metric_type: string;
  enrolled_count: number;
  attendance: {
    percentage: number;
    total_records: number;
  };
  assessment_count: number;
  assignment_completion_rate: number;
  total_assignments: number;
  submitted_assignments: number;
}

export interface FacultyAcademicOverview {
  data_source: string;
  metric_type: string;
  subjects_count: number;
  subjects: FacultySubjectSummary[];
}

export interface FacultyClassPattern {
  type: string;
  title: string;
  severity: string;
  description: string;
  supporting_data: string[];
}

export interface FacultyClassAssessmentItem {
  id: number;
  title: string;
  type: string;
  scheduled_at: string | null;
  max_marks: number;
  class_average_marks: number | null;
  class_average_pct: number | null;
  is_upcoming: boolean;
}

export interface FacultyClassOverview {
  data_source: string;
  metric_type: string;
  subject_id: number;
  code: string;
  name: string;
  credits: number;
  section: string;
  semester: number;
  enrolled_count: number;
  attendance: {
    percentage: number;
    present: number;
    absent: number;
    od: number;
    total: number;
    trend: {
      direction: string;
      from_pct: number;
      to_pct: number;
      change_pp: number;
      description: string;
    } | null;
  };
  assignments: {
    total: number;
    submitted: number;
    pending: number;
    overdue: number;
    completion_rate: number;
    prev_cycle_completion: number;
    change_pp: number;
  };
  assessments: {
    total_count: number;
    upcoming_count: number;
    completed_count: number;
    items: FacultyClassAssessmentItem[];
  };
  patterns: FacultyClassPattern[];
}

export interface FacultyClassTimeline {
  data_source: string;
  metric_type: string;
  subject_id: number;
  weekly_classes: {
    day: string;
    time: string;
    room?: string | null;
  }[];
  timeline_events: {
    category: string;
    title: string;
    type?: string;
    date: string | null;
    status?: string;
    max_marks?: number;
  }[];
}

export interface FacultyRelatedCase {
  case_id: string;
  category: string;
  description: string;
  status: string;
  priority: string;
  location?: string | null;
  created_at: string | null;
  is_related_to_course_infrastructure: boolean;
}

export interface ManagementAcademicOverview {
  data_source: string;
  metric_type: string;
  time_window: string;
  health_status: 'HEALTHY' | 'WATCH' | 'ELEVATED' | 'HIGH RISK';
  health_reasons: string[];
  total_subjects: number;
  total_departments: number;
  total_students: number;
  total_enrollments: number;
  overall_attendance_pct: number;
  total_attendance_records: number;
  attendance_present: number;
  attendance_absent: number;
  attendance_od: number;
  attendance_trend: {
    direction: string;
    from_pct: number;
    to_pct: number;
    change_pp: number;
    description: string;
  } | null;
  total_assessments: number;
  upcoming_assessments: number;
  total_assignments: number;
  submitted_assignments: number;
  pending_assignments: number;
  overdue_assignments: number;
  assignment_completion_rate: number;
  active_patterns_count: number;
}

export interface ManagementDepartmentSummary {
  department_id: number;
  department_name: string;
  department_code: string;
  subject_count: number;
  attendance_pct: number;
  attendance_records: number;
  assignment_completion_rate: number;
  total_assessments: number;
  trend: {
    direction: string;
    from_pct: number;
    to_pct: number;
    change_pp: number;
  } | null;
  data_sufficient: boolean;
  metric_type: string;
  data_source: string;
}

export interface ManagementDepartmentsResponse {
  data_source: string;
  metric_type: string;
  time_window: string;
  departments: ManagementDepartmentSummary[];
  total_departments: number;
}

export interface ManagementAcademicPattern {
  type: string;
  title: string;
  severity: string;
  description: string;
  supporting_data: string[];
}

export interface ManagementPatternsResponse {
  data_source: string;
  metric_type: string;
  patterns: ManagementAcademicPattern[];
}

// Proactive Intelligence Alerts
export interface AlertReasonData {
  priority: string;
  related_case_count: number;
  trend: string;
  unresolved_duration_days: number;
  location?: string;
  category?: string;
  department?: string;
  signals: string[];
}

export interface VignaiAlert {
  id: number;
  alert_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  message: string;
  case_group_id?: string;
  case_id?: string;
  department?: string;
  location?: string;
  status: 'NEW' | 'ACKNOWLEDGED' | 'RESOLVED' | 'DISMISSED';
  reason_data: AlertReasonData;
  target_route: string;
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  dismissed_at?: string;
}

export interface AlertActionResponse {
  id: number;
  status: string;
  message: string;
  updated_at?: string;
}


// Phase 8 Career Intelligence Interfaces
export interface CareerSkill {
  id?: number;
  name: string;
  skill_name?: string;
  category: 'TECHNICAL' | 'FRAMEWORK' | 'DATABASE' | 'TOOL' | 'SOFT_SKILL';
  source: 'VERIFIED_FROM_RESUME' | 'STUDENT_PROVIDED' | 'AI_ASSISTED_EXTRACTION';
  proficiency_level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
}

export interface CareerProject {
  id?: number;
  title: string;
  description?: string;
  technologies: string[];
  source: string;
}

export interface CareerCertification {
  id?: number;
  title: string;
  issuer?: string;
  issue_date?: string;
  source: string;
}

export interface CareerExperience {
  id?: number;
  title: string;
  organization?: string;
  duration?: string;
  description?: string;
  source: string;
}

export interface CareerProfile {
  id: number;
  student_id: number;
  headline?: string;
  summary?: string;
  education?: string;
  interests: string[];
  resume_file_name?: string;
  resume_file_size?: number;
  resume_uploaded_at?: string;
  extraction_status: 'NOT_UPLOADED' | 'COMPLETED' | 'FAILED';
  data_source: string;
  skills: CareerSkill[];
  projects: CareerProject[];
  certifications: CareerCertification[];
  experiences: CareerExperience[];
  created_at: string;
  updated_at: string;
}

export interface OpportunitySkill {
  id?: number;
  skill_name: string;
  is_required: boolean;
}

export interface Opportunity {
  id: number;
  opportunity_id: string;
  title: string;
  organization: string;
  opportunity_type: 'INTERNSHIP' | 'JOB' | 'RESEARCH' | 'HACKATHON' | 'COURSE' | 'CERTIFICATION';
  description: string;
  location: string;
  work_mode: 'REMOTE' | 'HYBRID' | 'ON_SITE';
  deadline?: string;
  eligibility: string;
  source_name?: string;
  source_type: string;
  verification_status?: 'DRAFT' | 'VERIFIED' | 'REJECTED' | 'EXPIRED';
  lifecycle_status?: 'NEW' | 'VERIFIED' | 'ACTIVE' | 'EXPIRING' | 'EXPIRED';
  submitted_at?: string;
  verified_at?: string;
  data_source: string;
  is_active: boolean;
  skills: OpportunitySkill[];
  created_at: string;
}

export interface OpportunityMatch {
  id: number;
  opportunity: Opportunity;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  location_fit: boolean;
  work_mode_fit: boolean;
  eligibility_fit: boolean;
  match_reasons: {
    score_breakdown?: {
      required_skills_weight?: string;
      required_matched?: string;
      preferred_skills_weight?: string;
      preferred_matched?: string;
      work_mode_fit_weight?: string;
      work_mode_status?: string;
    };
    matched_skills?: string[];
    missing_skills?: string[];
    eligibility_statement?: string;
    work_mode?: string;
    location?: string;
    key_factors?: string[];
    responsible_ai_disclaimer?: string;
  };
  is_closing_soon: boolean;
  days_remaining?: number | null;
  recommendation_text?: string;
}

export interface SkillGap {
  skill_name: string;
  occurrence_count: number;
  target_opportunities: string[];
  recommendation: string;
  category: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface DailyCareerBrief {
  student_name: string;
  total_matched_opportunities: number;
  top_match_title?: string;
  top_match_score?: number;
  top_match_org?: string;
  closing_soon_count: number;
  skill_gaps_count: number;
  skill_gaps: SkillGap[];
  brief_message: string;
  top_career_direction?: string;
  high_fit_count?: number;
  data_source: string;
}

export interface ResumeUploadResponse {
  message: string;
  file_name: string;
  file_size: number;
  extracted_skills_count: number;
  extracted_projects_count: number;
  profile: CareerProfile;
}


// Phase 8.5 Aggregation & Management Types
export interface OpportunitySource {
  id: number;
  source_name: string;
  source_type: 'INSTITUTION_CURATED' | 'AUTHORIZED_COORDINATOR' | 'APPROVED_API' | 'PUBLIC_FEED' | 'SYNTHETIC_DEVELOPMENT';
  status: 'HEALTHY' | 'DEGRADED' | 'OFFLINE';
  last_checked?: string;
  last_success?: string;
  items_found: number;
  error_message?: string;
  is_active: boolean;
  created_at: string;
}

export interface CoordinatorIntakeRequest {
  announcement_text: string;
  source_name?: string;
  source_type?: string;
}

export interface CoordinatorIntakeExtraction {
  title: string;
  organization: string;
  opportunity_type: string;
  description: string;
  skills_required: string[];
  skills_preferred: string[];
  eligibility: string;
  location: string;
  work_mode: string;
  deadline_str?: string;
}

export interface CoordinatorIntakeResponse {
  message: string;
  opportunity: Opportunity;
  extracted_details: CoordinatorIntakeExtraction;
}

export interface VerificationActionRequest {
  action: 'VERIFY' | 'REJECT';
  review_notes?: string;
}

export interface SyncSourcesResponse {
  message: string;
  total_sources_polled: number;
  new_opportunities_ingested: number;
  duplicates_skipped: number;
  expired_count: number;
  sources_health: OpportunitySource[];
}

// Phase 8.6 Career Fit & Personalized Recommendations Types
export interface CareerSubjectPerformance {
  code: string;
  name: string;
  score: number;
  credits: number;
}

export interface CareerDomainStrength {
  domain_id: string;
  domain_name: string;
  category: string;
  alignment_score: number;
  alignment_level: 'STRONG_ALIGNMENT' | 'GOOD_ALIGNMENT' | 'MODERATE_ALIGNMENT' | 'DEVELOPING_FIT';
  relevant_subjects: CareerSubjectPerformance[];
  matched_skills: string[];
  matching_projects_count: number;
  matching_certs_count: number;
  interest_matched: boolean;
  summary_phrase: string;
}

export interface CareerStrengthsResponse {
  student_name: string;
  top_career_direction: string;
  top_alignment_score: number;
  domain_strengths: CareerDomainStrength[];
  data_source: string;
}

export interface WhyRecommendedEvidence {
  primary_domain: string;
  domain_alignment_score: number;
  academic_highlights: string[];
  skill_highlights: string[];
  project_highlights: string;
  eligibility_statement: string;
  strengths: string[];
  skill_gaps: string[];
  learning_recommendation?: string;
  responsible_disclaimer: string;
}

export interface EligibilityEvaluation {
  status: 'ELIGIBLE' | 'INELIGIBLE' | 'UNKNOWN';
  is_eligible: boolean;
  reasons: string[];
  warnings: string[];
  criteria_summary: string;
}

export interface PersonalizedRecommendation {
  id: number;
  opportunity: Opportunity;
  match_score: number;
  personalized_profile_fit: number;
  eligibility: EligibilityEvaluation;
  matched_skills: string[];
  missing_skills: string[];
  primary_domain: string;
  why_recommended: WhyRecommendedEvidence;
  is_closing_soon: boolean;
  days_remaining?: number;
}

// Phase 8B VIIT Duvvada Context Interfaces
export interface ViitMetadata {
  institution_code: string;
  institution_name: string;
  short_name: string;
  campus_name: string;
  location: string;
  city: string;
  state: string;
  pincode: string;
  affiliation: string;
  accreditations: string[];
  data_provenance: string;
}

export interface ViitDepartment {
  code: string;
  name: string;
  category: string;
  programmes: string[];
  aliases: string[];
}

export interface ViitBuilding {
  name: string;
  code: string;
  description: string;
  facilities: string[];
  aliases: string[];
}

export interface ViitExamTerm {
  code: string;
  name: string;
  description: string;
  weightage?: string;
  aliases: string[];
}

export interface ViitRegulation {
  code: string;
  name: string;
  effective_years: string;
  credit_framework: string;
  description: string;
}

export interface ViitAttendancePolicyRule {
  label: string;
  range: string;
  description: string;
}

export interface ViitAttendancePolicy {
  normal_threshold_pct: number;
  condonation_min_pct: number;
  condonation_max_pct: number;
  detention_threshold_pct: number;
  rules: {
    NORMAL: ViitAttendancePolicyRule;
    CONDONATION_RANGE: ViitAttendancePolicyRule;
    DETENTION_WARNING: ViitAttendancePolicyRule;
  };
  policy_disclaimer: string;
}

export interface ViitInstitutionalContext {
  metadata: ViitMetadata;
  departments_count: number;
  departments: ViitDepartment[];
  regulations: ViitRegulation[];
  exam_terms: ViitExamTerm[];
  attendance_policy: ViitAttendancePolicy;
  campus_buildings: ViitBuilding[];
  statutory_cells: Array<{ name: string; code: string; jurisdiction: string }>;
  transport_routes: { fleet_description: string; key_commute_areas: string[]; disclaimer: string };
  connector_statuses: Record<string, string>;
  provenance: string;
  timestamp: string;
}

// Phase 9 Cross-Domain Intelligence & Proactive Insight Engine
export interface InsightSignal {
  domain: string;
  metric: string;
  value: string;
  source: string;
}

export interface InsightEvidence {
  signals: InsightSignal[];
  details?: Record<string, any>;
  conclusion?: string;
}

export interface InsightAction {
  label: string;
  url: string;
  action_type: string;
  description?: string;
}

export interface VignaiInsight {
  id: number;
  insight_type: string;
  severity: 'INFO' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  summary: string;
  role: string;
  target_user_id?: number;
  target_department?: string;
  status: 'NEW' | 'SEEN' | 'ACTIONED' | 'DISMISSED' | 'EXPIRED';
  source_domains: string[];
  evidence: InsightEvidence;
  recommended_action: InsightAction;
  created_at: string;
  expires_at?: string;
  deduplication_key: string;
}

// Phase 10 — Action Intelligence ("From Insights to Decisions")
export interface ActionPriorityEvidence {
  urgency: number;
  impact: number;
  evidence_strength: number;
  relevance: number;
  signals: Array<{ domain?: string; metric: string; value: string; source: string }>;
  why_first: string[];
  conclusion?: string;
}

export interface VignaiAction {
  id: number;
  action_type: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  priority_score: number;
  title: string;
  summary: string;
  role: string;
  target_user_id?: number;
  target_department?: string;
  source_insight_id?: number;
  source_domain: string;
  evidence: ActionPriorityEvidence;
  recommended_action: InsightAction;
  target_route: string;
  ask_vignai_query?: string;
  status: 'NEW' | 'SEEN' | 'IN_PROGRESS' | 'COMPLETED' | 'DISMISSED' | 'EXPIRED';
  created_at: string;
  expires_at?: string;
  deduplication_key: string;
}

export interface ActionDailySummary {
  role: string;
  greeting: string;
  total_priorities: number;
  top_priority_title?: string;
  highlights: string[];
  actions: VignaiAction[];
}
