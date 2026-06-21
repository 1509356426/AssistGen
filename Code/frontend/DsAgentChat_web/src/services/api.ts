import { ChatMessage } from '../types'
import axios from './axios'
import router from '../router'
import { sha256 } from '../utils/crypto'
import { readSSEStream } from '../utils/sse'

// 接口定义
interface StreamChunk {
  type?: 'think' | 'response'
  content: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
}

export interface UserLogin {
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface Conversation {
  id: number
  created_at: string
  title: string
  status: 'ongoing' | 'completed'
  dialogue_type: string
}

export interface Message {
  id: number
  conversation_id: number
  sender: 'user' | 'assistant'
  content: string
  created_at: string
  message_type: string
}

export class ApiService {
  static baseUrl = import.meta.env.VITE_API_BASE_URL || ''

  static buildUrl(path: string) {
    return `${this.baseUrl}${path}`
  }

  // 处理带跨分片缓冲的聊天消息流
  static async handleChatStream(reader: ReadableStreamDefaultReader<Uint8Array>, 
                              onChunk: (chunk: StreamChunk) => void) {
    let fullContent = ''

    try {
      await readSSEStream(reader, (data) => {
        const parsed = JSON.parse(data)
        if (typeof parsed === 'object' && parsed?.type === 'error') {
          throw new Error(parsed.message || '流式响应失败')
        }
        if (typeof parsed !== 'string') return

        fullContent += parsed
        const thinkStart = fullContent.indexOf('<think>')
        const thinkEnd = fullContent.indexOf('</think>')

        if (thinkStart !== -1) {
          const end = thinkEnd === -1 ? fullContent.length : thinkEnd
          onChunk({
            type: 'think',
            content: fullContent.slice(thinkStart + '<think>'.length, end),
          })
          if (thinkEnd !== -1) {
            onChunk({
              type: 'response',
              content: fullContent.slice(thinkEnd + '</think>'.length),
            })
          }
        } else if (!'<think>'.startsWith(fullContent)) {
          onChunk({ type: 'response', content: fullContent })
        }
      })
    } catch (error) {
      console.error('Error reading stream:', error)
      throw error
    }
  }

  // 创建新会话
  static async createConversation(): Promise<number> {
    const response = await fetch(this.buildUrl('/api/conversations'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        user_id: localStorage.getItem('user_id')
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data.conversation_id
  }

  // 聊天接口
  static async chat(messages: ChatMessage[], conversationId: number) {
    if (!conversationId) {
      throw new Error('Missing conversation_id')
    }

    const response = await fetch(this.buildUrl('/api/chat'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        messages,
        user_id: localStorage.getItem('user_id'),
        conversation_id: conversationId
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.body?.getReader()
  }

  // 推理接口
  static async reason(messages: ChatMessage[], conversationId: number) {
    if (!conversationId) {
      throw new Error('Missing conversation_id')
    }

    const response = await fetch(this.buildUrl('/api/reason'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        messages,
        user_id: localStorage.getItem('user_id'),
        conversation_id: conversationId
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.body?.getReader()
  }

  // 搜索接口
  static async search(messages: ChatMessage[], conversationId: number) {
    if (!conversationId) {
      throw new Error('Missing conversation_id')
    }

    const response = await fetch(this.buildUrl('/api/search'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        messages,
        user_id: localStorage.getItem('user_id'),
        conversation_id: conversationId
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.body?.getReader()
  }

  // 获取用户的所有会话
  static async getUserConversations(userId: string): Promise<Conversation[]> {
    const response = await fetch(this.buildUrl(`/api/conversations/user/${userId}`), {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // 获取特定会话的所有消息
  static async getConversationMessages(conversationId: number): Promise<Message[]> {
    const userId = localStorage.getItem('user_id')
    const response = await fetch(this.buildUrl(`/api/conversations/${conversationId}/messages?user_id=${userId}`), {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // 删除会话
  static async deleteConversation(conversationId: number): Promise<void> {
    const response = await fetch(this.buildUrl(`/api/conversations/${conversationId}`), {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
  }

  // 更新会话名称
  static async updateConversationName(conversationId: number, name: string): Promise<void> {
    const response = await fetch(this.buildUrl(`/api/conversations/${conversationId}/name`), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ name })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
  }
}

export const AuthService = {
  async register(data: UserCreate): Promise<Token> {
    const hashedPassword = await sha256(data.password)
    const response = await axios.post('/api/register', {
      username: data.username,
      email: data.email,
      password: hashedPassword
    })
    return response.data
  },

  async login(data: UserLogin): Promise<Token> {
    const hashedPassword = await sha256(data.password)
    const response = await axios.post('/api/token', {
      email: data.email,
      password: hashedPassword
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async logout() {
    localStorage.removeItem('token')
    router.push('/login')
  },

  async validateToken() {
    try {
      await axios.get('/api/validate-token')
      return true
    } catch {
      return false
    }
  },

  async getUserInfo() {
    const response = await axios.get('/api/users/me')
    return response.data
  }
}
