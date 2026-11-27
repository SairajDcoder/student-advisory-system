import React, { useEffect, useState } from 'react'
import { Award, BookOpen, Lightbulb, Save } from 'lucide-react'
import { AppShell } from '../components/AppShell'
import { Card } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { apiRequest } from '../lib/api'

export function SettingsPage() {
  const { user, theme, setThemeMode, refreshUser } = useAuth()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [department, setDepartment] = useState(user?.department || '')
  const [educationStage, setEducationStage] = useState(user?.education_stage || '12th')
  const [stream, setStream] = useState(user?.stream || 'Science (PCM)')
  const [language, setLanguage] = useState(user?.language_preference || 'en')
  const [notificationsEnabled, setNotificationsEnabled] = useState(
    user?.notifications_enabled ?? true
  )

  // Academic Information
  const [studyHoursPerWeek, setStudyHoursPerWeek] = useState(
    user?.study_hours_per_week ?? 25
  )
  const [attendancePct, setAttendancePct] = useState(user?.attendance_pct ?? 75)
  const [previousGpa, setPreviousGpa] = useState(user?.previous_gpa ?? 3.2)
  const [mathScore, setMathScore] = useState(user?.math_score ?? 70)
  const [scienceScore, setScienceScore] = useState(user?.science_score ?? 65)
  const [englishScore, setEnglishScore] = useState(user?.english_score ?? 72)

  // Skills & Aptitude
  const [programmingScore, setProgrammingScore] = useState(user?.programming_score ?? 60)
  const [creativityScore, setCreativityScore] = useState(user?.creativity_score ?? 55)
  const [communicationScore, setCommunicationScore] = useState(
    user?.communication_score ?? 65
  )
  const [leadershipScore, setLeadershipScore] = useState(user?.leadership_score ?? 50)

  // Experience & Background
  const [extracurricularActivities, setExtracurricularActivities] = useState(
    user?.extracurricular_activities ?? 2
  )
  const [internshipExperience, setInternshipExperience] = useState(
    user?.internship_experience ?? 0
  )
  const [projectsCompleted, setProjectsCompleted] = useState(user?.projects_completed ?? 3)
  const [gender, setGender] = useState(user?.gender || 'Male')
  const [parentalEducation, setParentalEducation] = useState(
    user?.parental_education || 'High School'
  )
  const [partTimeJob, setPartTimeJob] = useState(user?.part_time_job ?? 0)

  const [saved, setSaved] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!user) return
    setFullName(user.full_name || '')
    setDepartment(user.department || '')
    setEducationStage(user.education_stage || '12th')
    setStream(user.stream || 'Science (PCM)')
    setLanguage(user.language_preference || 'en')
    setNotificationsEnabled(user.notifications_enabled ?? true)
    setStudyHoursPerWeek(user.study_hours_per_week ?? 25)
    setAttendancePct(user.attendance_pct ?? 75)
    setPreviousGpa(user.previous_gpa ?? 3.2)
    setMathScore(user.math_score ?? 70)
    setScienceScore(user.science_score ?? 65)
    setEnglishScore(user.english_score ?? 72)
    setProgrammingScore(user.programming_score ?? 60)
    setCreativityScore(user.creativity_score ?? 55)
    setCommunicationScore(user.communication_score ?? 65)
    setLeadershipScore(user.leadership_score ?? 50)
    setExtracurricularActivities(user.extracurricular_activities ?? 2)
    setInternshipExperience(user.internship_experience ?? 0)
    setProjectsCompleted(user.projects_completed ?? 3)
    setGender(user.gender || 'Male')
    setParentalEducation(user.parental_education || 'High School')
    setPartTimeJob(user.part_time_job ?? 0)
  }, [user])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setSaved('')
    setError('')
    try {
      const payload: Record<string, unknown> = {
        full_name: fullName,
        department,
        education_stage: educationStage,
        stream,
        theme_preference: theme,
        language_preference: language,
        notifications_enabled: notificationsEnabled,
      }
      if (user?.role === 'student') {
        Object.assign(payload, {
          study_hours_per_week: Number(studyHoursPerWeek),
          attendance_pct: Number(attendancePct),
          previous_gpa: Number(previousGpa),
          math_score: Number(mathScore),
          science_score: Number(scienceScore),
          english_score: Number(englishScore),
          programming_score: Number(programmingScore),
          creativity_score: Number(creativityScore),
          communication_score: Number(communicationScore),
          leadership_score: Number(leadershipScore),
          extracurricular_activities: Number(extracurricularActivities),
          internship_experience: Number(internshipExperience),
          projects_completed: Number(projectsCompleted),
          gender,
          parental_education: parentalEducation,
          part_time_job: Number(partTimeJob),
        })
      }

      await apiRequest('/api/profile', {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })
      await refreshUser()
      setSaved(
        'Your profile, academic scores, and preferences have been saved and AI insights refreshed.'
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save profile changes.')
    } finally {
      setSaving(false)
    }
  }

  const inputClass =
    'mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800'

  return (
    <AppShell>
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="rounded-2xl bg-gradient-to-r from-[#7B2D8E] to-[#581C68] p-6 text-white shadow-md">
          <h1 className="font-['Poppins'] text-2xl font-bold">Profile &amp; Settings</h1>
          <p className="mt-1 text-base text-purple-100">
            Manage your academic scores, skills, background, 10th/12th track, and app preferences.
          </p>
        </div>

        <Card>
          <form onSubmit={handleSave} className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm font-semibold">Full Name</span>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className={inputClass}
                  required
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold">Department / Track</span>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className={inputClass}
                />
              </label>
            </div>

            {user?.role === 'student' && (
              <>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <label className="block">
                    <span className="text-sm font-semibold">Education Stage</span>
                    <select
                      value={educationStage || '12th'}
                      onChange={(e) =>
                        setEducationStage(e.target.value as '10th' | '12th' | 'college')
                      }
                      className={inputClass}
                    >
                      <option value="10th">10th Pass-Out</option>
                      <option value="12th">12th Pass-Out</option>
                      <option value="college">College</option>
                    </select>
                  </label>

                  <label className="block">
                    <span className="text-sm font-semibold">Stream</span>
                    <select
                      value={stream || 'Science (PCM)'}
                      onChange={(e) => setStream(e.target.value)}
                      className={inputClass}
                    >
                      <option>General</option>
                      <option>Science (PCM)</option>
                      <option>Science (PCB)</option>
                      <option>Commerce</option>
                      <option>Arts</option>
                    </select>
                  </label>
                </div>

                {/* Section 1: Academic Information */}
                <div className="space-y-4 border-t border-slate-200 pt-5 dark:border-slate-800">
                  <div className="flex items-center gap-2 text-[#7B2D8E] dark:text-purple-300">
                    <BookOpen className="h-5 w-5" aria-hidden="true" />
                    <h2 className="font-['Poppins'] text-lg font-bold">Academic Information</h2>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <label className="block">
                      <span className="text-sm font-semibold">Study Hours per Week</span>
                      <input
                        type="number"
                        min={0}
                        max={80}
                        step={0.5}
                        value={studyHoursPerWeek}
                        onChange={(e) => setStudyHoursPerWeek(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Attendance (%)</span>
                      <input
                        type="number"
                        min={0}
                        max={100}
                        step={0.1}
                        value={attendancePct}
                        onChange={(e) => setAttendancePct(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Previous GPA (2.0 – 4.0)</span>
                      <input
                        type="number"
                        min={0}
                        max={4}
                        step={0.01}
                        value={previousGpa}
                        onChange={(e) => setPreviousGpa(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Math Score (0 – 100)</span>
                      <input
                        type="number"
                        min={0}
                        max={100}
                        value={mathScore}
                        onChange={(e) => setMathScore(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Science Score (0 – 100)</span>
                      <input
                        type="number"
                        min={0}
                        max={100}
                        value={scienceScore}
                        onChange={(e) => setScienceScore(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">English Score (0 – 100)</span>
                      <input
                        type="number"
                        min={0}
                        max={100}
                        value={englishScore}
                        onChange={(e) => setEnglishScore(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>
                  </div>
                </div>

                {/* Section 2: Skills & Aptitude */}
                <div className="space-y-4 border-t border-slate-200 pt-5 dark:border-slate-800">
                  <div className="flex items-center gap-2 text-[#7B2D8E] dark:text-purple-300">
                    <Lightbulb className="h-5 w-5" aria-hidden="true" />
                    <h2 className="font-['Poppins'] text-lg font-bold">Skills &amp; Aptitude</h2>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <label className="block">
                      <span className="text-sm font-semibold">Programming Score (0 – 100)</span>
                      <input
                        type="number"
                        min={0}
                        max={100}
                        value={programmingScore}
                        onChange={(e) => setProgrammingScore(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Creativity Score (0 – 100)</span>
                      <input
                        type="number"
                        min={0}
                        max={100}
                        value={creativityScore}
                        onChange={(e) => setCreativityScore(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Communication Score (0 – 100)</span>
                      <input
                        type="number"
                        min={0}
                        max={100}
                        value={communicationScore}
                        onChange={(e) => setCommunicationScore(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Leadership Score (0 – 100)</span>
                      <input
                        type="number"
                        min={0}
                        max={100}
                        value={leadershipScore}
                        onChange={(e) => setLeadershipScore(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>
                  </div>
                </div>

                {/* Section 3: Experience & Background */}
                <div className="space-y-4 border-t border-slate-200 pt-5 dark:border-slate-800">
                  <div className="flex items-center gap-2 text-[#7B2D8E] dark:text-purple-300">
                    <Award className="h-5 w-5" aria-hidden="true" />
                    <h2 className="font-['Poppins'] text-lg font-bold">
                      Experience &amp; Background
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <label className="block">
                      <span className="text-sm font-semibold">
                        Extracurricular Activities (0 – 5)
                      </span>
                      <input
                        type="number"
                        min={0}
                        max={5}
                        value={extracurricularActivities}
                        onChange={(e) => setExtracurricularActivities(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Internship Experience</span>
                      <select
                        value={internshipExperience}
                        onChange={(e) => setInternshipExperience(Number(e.target.value))}
                        className={inputClass}
                      >
                        <option value={0}>No</option>
                        <option value={1}>Yes</option>
                      </select>
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Projects Completed (0 – 10)</span>
                      <input
                        type="number"
                        min={0}
                        max={10}
                        value={projectsCompleted}
                        onChange={(e) => setProjectsCompleted(Number(e.target.value))}
                        className={inputClass}
                        required
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Gender</span>
                      <select
                        value={gender}
                        onChange={(e) => setGender(e.target.value)}
                        className={inputClass}
                      >
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Parental Education</span>
                      <select
                        value={parentalEducation}
                        onChange={(e) => setParentalEducation(e.target.value)}
                        className={inputClass}
                      >
                        <option value="High School">High School</option>
                        <option value="Bachelor">Bachelor</option>
                        <option value="Master">Master</option>
                        <option value="PhD">PhD</option>
                      </select>
                    </label>

                    <label className="block">
                      <span className="text-sm font-semibold">Part-Time Job</span>
                      <select
                        value={partTimeJob}
                        onChange={(e) => setPartTimeJob(Number(e.target.value))}
                        className={inputClass}
                      >
                        <option value={0}>No</option>
                        <option value={1}>Yes</option>
                      </select>
                    </label>
                  </div>
                </div>
              </>
            )}

            <div className="grid grid-cols-1 gap-4 border-t border-slate-200 pt-5 sm:grid-cols-2 dark:border-slate-800">
              <label className="block">
                <span className="text-sm font-semibold">Theme Mode</span>
                <select
                  value={theme}
                  onChange={(e) => setThemeMode(e.target.value as 'light' | 'dark')}
                  className={inputClass}
                >
                  <option value="light">Light Mode</option>
                  <option value="dark">Dark Mode</option>
                </select>
              </label>

              <label className="block">
                <span className="text-sm font-semibold">Language</span>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className={inputClass}
                >
                  <option value="en">English</option>
                  <option value="hi">Hindi (हिन्दी)</option>
                  <option value="mr">Marathi (मराठी)</option>
                </select>
              </label>
            </div>

            <label className="flex items-center justify-between rounded-xl border border-slate-200 p-4 dark:border-slate-700">
              <div>
                <p className="text-base font-semibold">Smart Alerts &amp; Notifications</p>
                <p className="text-sm text-slate-500">
                  Attendance alerts, exam deadlines, and new AI career updates
                </p>
              </div>
              <input
                type="checkbox"
                checked={notificationsEnabled}
                onChange={(e) => setNotificationsEnabled(e.target.checked)}
                className="h-5 w-5 accent-[#7B2D8E]"
              />
            </label>

            {error && (
              <p className="rounded-xl bg-rose-50 px-4 py-2.5 text-sm font-semibold text-rose-700 dark:bg-rose-950/50 dark:text-rose-300">
                {error}
              </p>
            )}

            {saved && (
              <p className="rounded-xl bg-emerald-50 px-4 py-2.5 text-sm font-semibold text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">
                {saved}
              </p>
            )}

            <button
              type="submit"
              disabled={saving}
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#FF7A45] to-[#FF5163] py-3.5 text-base font-bold text-white shadow-sm hover:brightness-105 disabled:opacity-60"
            >
              <Save className="h-5 w-5" aria-hidden="true" />
              <span>{saving ? 'Saving...' : 'Save Profile & Settings'}</span>
            </button>
          </form>
        </Card>
      </div>
    </AppShell>
  )
}
