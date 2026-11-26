import React, { useEffect, useRef, useState } from 'react'
import { Bot, Mic, MicOff, Send, User } from 'lucide-react'
import { AppShell } from '../components/AppShell'
import { Card } from '../components/ui'
import { apiRequest } from '../lib/api'
import { ChatMsg } from '../types'

const SUGGESTED_QUESTIONS = [
  'How can I improve my CGPA?',
  'Which stream or career suits me after 10th/12th?',
  'How should I use my weekly study plan?',
  'I feel stressed about upcoming exams',
]

export function ChatAdvisorPage() {
  const [messages, setMessages] = useState<ChatMsg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [typing, setTyping] = useState(false)
  const [listening, setListening] = useState(false)
  const bottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    apiRequest<ChatMsg[]>('/api/student/chat')
      .then(setMessages)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typing])

  const sendMessage = async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || typing) return
    setInput('')

    const tempUser: ChatMsg = {
      id: Date.now(),
      sender: 'user',
      message: trimmed,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, tempUser])
    setTyping(true)

    try {
      const res = await apiRequest<{ user_message: ChatMsg; assistant_message: ChatMsg }>(
        '/api/student/chat',
        {
          method: 'POST',
          body: JSON.stringify({ message: trimmed }),
        }
      )
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUser.id),
        res.user_message,
        res.assistant_message,
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'assistant',
          message: 'Sorry, I had trouble reaching the server. Please try again in a moment.',
          created_at: new Date().toISOString(),
        },
      ])
    } finally {
      setTyping(false)
    }
  }

  const startVoice = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert('Voice input is supported in Chrome or Edge browsers.')
      return
    }
    const recognition = new SpeechRecognition()
    recognition.lang = 'en-IN'
    setListening(true)
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      setInput((prev) => (prev ? `${prev} ${transcript}` : transcript))
    }
    recognition.onend = () => setListening(false)
    recognition.onerror = () => setListening(false)
    recognition.start()
  }

  return (
    <AppShell>
      <div className="mx-auto flex h-[calc(100vh-11rem)] max-w-4xl flex-col gap-4">
        <div className="rounded-2xl bg-gradient-to-r from-[#7B2D8E] to-[#581C68] px-6 py-4 text-white shadow-sm">
          <h1 className="font-['Poppins'] text-2xl font-bold">Chat with AdvisorAI</h1>
          <p className="text-sm text-purple-100">
            Ask doubts about 10th/12th streams, subjects, or career choices — like texting a friendly mentor.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => sendMessage(q)}
              className="rounded-full border border-purple-200 bg-purple-50 px-3.5 py-1.5 text-sm font-semibold text-[#7B2D8E] transition hover:bg-purple-100 dark:border-purple-900 dark:bg-purple-950/60 dark:text-purple-200"
            >
              {q}
            </button>
          ))}
        </div>

        <Card className="flex min-h-0 flex-1 flex-col p-0">
          <div className="flex-1 space-y-4 overflow-y-auto p-5">
            {loading ? (
              <p className="text-center text-sm text-slate-500">Loading conversation...</p>
            ) : (
              messages.map((m) => {
                const isUser = m.sender === 'user'
                return (
                  <div
                    key={m.id}
                    className={`flex items-end gap-2.5 ${isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    {!isUser && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#14B8A6] text-white">
                        <Bot className="h-4 w-4" aria-hidden="true" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] whitespace-pre-line rounded-2xl px-4 py-3 text-base leading-relaxed shadow-sm ${
                        isUser
                          ? 'rounded-br-sm bg-gradient-to-r from-[#7B2D8E] to-[#632275] text-white'
                          : 'rounded-bl-sm bg-[#FAF7FD] text-slate-900 dark:bg-slate-800 dark:text-slate-100'
                      }`}
                    >
                      {m.message}
                    </div>
                    {isUser && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-orange-100 text-[#FF6B4A] dark:bg-slate-700 dark:text-slate-200">
                        <User className="h-4 w-4" aria-hidden="true" />
                      </div>
                    )}
                  </div>
                )
              })
            )}

            {typing && (
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#14B8A6] text-white">
                  <Bot className="h-4 w-4" aria-hidden="true" />
                </div>
                <div className="rounded-2xl bg-[#FAF7FD] px-4 py-3 text-sm font-medium text-slate-500 dark:bg-slate-800">
                  AdvisorAI is typing...
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault()
              sendMessage(input)
            }}
            className="flex items-center gap-2 border-t border-purple-100 p-3 dark:border-slate-800"
          >
            <button
              type="button"
              onClick={startVoice}
              className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-2.5 text-sm font-semibold ${
                listening
                  ? 'border-rose-400 bg-rose-50 text-rose-600'
                  : 'border-slate-200 text-slate-600 hover:bg-purple-50 dark:border-slate-700 dark:text-slate-300'
              }`}
            >
              {listening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              <span className="hidden sm:inline">{listening ? 'Listening' : 'Voice'}</span>
            </button>

            <input
              type="text"
              aria-label="Ask AdvisorAI a question"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your question here..."
              className="flex-1 rounded-xl border border-slate-200 bg-[#FAF7FD] px-4 py-2.5 text-base focus:border-[#7B2D8E] focus:bg-white focus:outline-none dark:border-slate-700 dark:bg-slate-800"
            />

            <button
              type="submit"
              disabled={!input.trim() || typing}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#FF7A45] to-[#FF5163] px-5 py-2.5 text-base font-bold text-white shadow-sm hover:brightness-105 disabled:opacity-50"
            >
              <Send className="h-4 w-4" aria-hidden="true" />
              <span>Send</span>
            </button>
          </form>
        </Card>
      </div>
    </AppShell>
  )
}
