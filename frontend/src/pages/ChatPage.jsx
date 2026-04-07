import { useState } from 'react'
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material'
import { Send } from '@mui/icons-material'
import { queryDocuments } from '../api/client'

export default function ChatPage() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSend = async () => {
    if (!question.trim()) return

    const userMessage = { role: 'user', content: question }
    setMessages((prev) => [...prev, userMessage])
    setQuestion('')
    setLoading(true)
    setError(null)

    try {
      const response = await queryDocuments(question)
      
      const botMessage = {
        role: 'assistant',
        content: response.answer,
        citations: response.citations || [],
        model: response.model_used,
      }
      setMessages((prev) => [...prev, botMessage])
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Query failed')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Chat & Query
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Ask questions about legal documents with evidence-based answers
        </Typography>

        <Box
          sx={{
            height: '400px',
            overflowY: 'auto',
            border: '1px solid #ddd',
            borderRadius: 1,
            p: 2,
            mb: 2,
            bgcolor: '#f9f9f9',
          }}
        >
          {messages.length === 0 && (
            <Typography variant="body2" color="text.secondary" align="center">
              Start a conversation...
            </Typography>
          )}

          {messages.map((msg, index) => (
            <Box
              key={index}
              sx={{
                mb: 2,
                p: 2,
                borderRadius: 1,
                bgcolor: msg.role === 'user' ? '#e3f2fd' : '#fff',
                border: '1px solid',
                borderColor: msg.role === 'user' ? '#2196f3' : '#ddd',
              }}
            >
              <Typography variant="caption" color="text.secondary">
                {msg.role === 'user' ? 'You' : 'Chatbot'}
              </Typography>
              <Typography variant="body1" sx={{ mt: 0.5, whiteSpace: 'pre-wrap' }}>
                {msg.content}
              </Typography>

              {msg.citations && msg.citations.length > 0 && (
                <>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="caption" color="text.secondary">
                    Citations:
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    {msg.citations.map((citation, idx) => (
                      <Chip
                        key={idx}
                        label={`${citation.source}${citation.article_ref ? ` - ${citation.article_ref}` : ''}`}
                        size="small"
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </Box>
                </>
              )}
            </Box>
          ))}

          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            placeholder="Ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <Button
            variant="contained"
            endIcon={<Send />}
            onClick={handleSend}
            disabled={!question.trim() || loading}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Container>
  )
}
