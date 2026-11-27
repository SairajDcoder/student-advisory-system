export type Role = 'student' | 'mentor' | 'admin'

export interface User {
  id: number
  email: string
  full_name: string
  role: Role
  department: string
  theme_preference: 'light' | 'dark'
  language_preference: string
  notifications_enabled: boolean
  onboarding_completed: boolean
  education_stage?: '10th' | '12th' | 'college' | null
  stream?: string | null
  study_hours_per_week?: number | null
  attendance_pct?: number | null
  previous_gpa?: number | null
  math_score?: number | null
  science_score?: number | null
  english_score?: number | null
  programming_score?: number | null
  creativity_score?: number | null
  communication_score?: number | null
  leadership_score?: number | null
  extracurricular_activities?: number | null
  internship_experience?: number | null
  projects_completed?: number | null
  gender?: string | null
  parental_education?: string | null
  part_time_job?: number | null
}

export interface ExplainFactor {
  key: string
  factor: string
  value: number
  impact: number
  signed_shap: number
  direction: 'positive' | 'negative'
  plain_text: string
}

export interface SubjectScore {
  id: number
  code: string
  subject: string
  internal: number
  assignment: number
  exam: number
  attendance: number
  weak_area: boolean
  exam_date: string
}

export interface StudentDashboardData {
  student: {
    id: number
    full_name: string
    education_stage: string
    board_name: string
    stream: string
    department: string
    board_percentage: number
    current_cgpa: number
    attendance_pct: number
    internal_marks_avg: number
    assignment_score_avg: number
    study_hours_per_week: number
    upcoming_deadlines_count: number
    previous_grades: { term: string; cgpa: number }[]
    goals: string
    mentor_remarks: string
    next_meeting_at: string
    onboarding_completed: boolean
  }
  prediction: {
    predicted_cgpa: number
    pass_probability: number
    risk_level: 'Low' | 'Medium' | 'High'
    risk_score: number
    top_reasons: ExplainFactor[]
    ai_insights: string[]
  }
  subject_scores: SubjectScore[]
  unread_notifications: number
}

export interface CareerItem {
  id: number
  title: string
  match_pct: number
  summary: string
  required_skills: string[]
  skill_gaps: { skill: string; current: number; target: number }[]
  suggested_courses: { title: string; provider: string; duration: string; type: string }[]
}

export interface CareersResponse {
  education_stage: string
  stream: string
  stream_recommendation: {
    title: string
    match_pct: number
    summary: string
  } | null
  careers: CareerItem[]
}

export interface ChatMsg {
  id: number
  sender: 'user' | 'assistant'
  message: string
  created_at: string
}

export interface StudyTask {
  id: number
  day_of_week: string
  subject: string
  topic: string
  duration_minutes: number
  priority: 'high' | 'medium' | 'low'
  completed: boolean
  order_index: number
}

export interface CheckinItem {
  id: number
  mood: string
  stress_score: number
  sleep_hours: number
  supportive_message: string
  wants_mentor_talk: boolean
  created_at: string
}

export interface NotificationItem {
  id: number
  title: string
  message: string
  category: string
  is_read: boolean
  created_at: string
}

export interface MentorStudent {
  student_id: number
  full_name: string
  email: string
  education_stage: string
  stream: string
  department: string
  current_cgpa: number
  predicted_cgpa: number
  attendance_pct: number
  internal_marks_avg: number
  risk_level: 'Low' | 'Medium' | 'High'
  risk_score: number
  top_reasons: ExplainFactor[]
  ai_insights: string[]
  mentor_remarks: string
  next_meeting_at: string
  wants_mentor_talk: boolean
  latest_mood: string
  subjects: { name: string; internal: number; exam: number; weak_area: boolean }[]
}

export interface AdminOverview {
  users: {
    id: number
    full_name: string
    email: string
    role: Role
    department: string
    is_active: boolean
  }[]
  department_analytics: {
    department: string
    students: number
    avg_cgpa: number
    at_risk: number
  }[]
  risk_summary: Record<'Low' | 'Medium' | 'High', number>
  system_health: {
    api_status: string
    database_status: string
    total_users: number
    total_students: number
    ml_metrics: Record<string, any>
  }
}
