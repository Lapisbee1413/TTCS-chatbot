import { useState, useEffect, useRef } from 'react'
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Switch,
  FormControlLabel,
  Divider,
} from '@mui/material'
import { listDocuments, getDocumentContent } from '../api/client'

export default function ParallelViewPage() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedV1, setSelectedV1] = useState('')
  const [selectedV2, setSelectedV2] = useState('')
  const [syncScroll, setSyncScroll] = useState(true)
  const [v1Content, setV1Content] = useState([])
  const [v2Content, setV2Content] = useState([])
  
  const scrollRef1 = useRef(null)
  const scrollRef2 = useRef(null)
  const isScrolling = useRef(false)

  useEffect(() => {
    loadDocuments()
  }, [])

  useEffect(() => {
    if (selectedV1) {
      loadDocumentContent(selectedV1, setV1Content)
    }
  }, [selectedV1])

  useEffect(() => {
    if (selectedV2) {
      loadDocumentContent(selectedV2, setV2Content)
    }
  }, [selectedV2])

  const loadDocuments = async () => {
    try {
      const response = await listDocuments()
      setDocuments(response.documents || [])
      
      // Auto-select first 2 documents if available
      if (response.documents && response.documents.length >= 2) {
        setSelectedV1(response.documents[0].source)
        setSelectedV2(response.documents[1].source)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const loadDocumentContent = async (source, setContent) => {
    try {
      const response = await getDocumentContent(source)
      setContent(response.articles || [])
    } catch (err) {
      console.error(`Error loading content for ${source}:`, err)
      setContent([{
        article: 'Error',
        content: `Khong the load noi dung: ${err.message}`
      }])
    }
  }

  const handleScroll = (sourceRef, targetRef) => (event) => {
    if (!syncScroll || isScrolling.current) return
    
    isScrolling.current = true
    const source = event.target
    const scrollPercentage = source.scrollTop / (source.scrollHeight - source.clientHeight)
    
    if (targetRef.current) {
      const targetScrollTop = scrollPercentage * (targetRef.current.scrollHeight - targetRef.current.clientHeight)
      targetRef.current.scrollTop = targetScrollTop
    }
    
    setTimeout(() => {
      isScrolling.current = false
    }, 50)
  }

  const getDifferences = (text1, text2) => {
    // Simple diff highlighting - in production use a proper diff library
    if (text1 === text2) return { type: 'same', text: text1 }
    if (!text1) return { type: 'added', text: text2 }
    if (!text2) return { type: 'removed', text: text1 }
    return { type: 'modified', text: text1 }
  }

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    )
  }

  if (documents.length < 2) {
    return (
      <Container>
        <Alert severity="warning">
          You need at least 2 documents uploaded to use parallel view. Please upload documents first.
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        Parallel View
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        View two document versions side-by-side
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={5}>
            <FormControl fullWidth>
              <InputLabel>Version 1</InputLabel>
              <Select value={selectedV1} onChange={(e) => setSelectedV1(e.target.value)} label="Version 1">
                {documents.map((doc) => (
                  <MenuItem key={doc.source} value={doc.source}>
                    {doc.source} ({doc.num_chunks} chunks)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2} sx={{ textAlign: 'center' }}>
            <FormControlLabel
              control={<Switch checked={syncScroll} onChange={(e) => setSyncScroll(e.target.checked)} />}
              label="Sync Scroll"
            />
          </Grid>
          <Grid item xs={12} md={5}>
            <FormControl fullWidth>
              <InputLabel>Version 2</InputLabel>
              <Select value={selectedV2} onChange={(e) => setSelectedV2(e.target.value)} label="Version 2">
                {documents.map((doc) => (
                  <MenuItem key={doc.source} value={doc.source}>
                    {doc.source} ({doc.num_chunks} chunks)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Paper 
            elevation={3} 
            sx={{ 
              height: '600px', 
              overflow: 'auto',
              border: syncScroll ? '2px solid #1976d2' : 'none'
            }}
            ref={scrollRef1}
            onScroll={handleScroll(scrollRef1, scrollRef2)}
          >
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom color="primary">
                {selectedV1}
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {v1Content.map((item, index) => {
                const v2Item = v2Content[index]
                const diff = v2Item ? getDifferences(item.content, v2Item.content) : { type: 'removed' }
                
                return (
                  <Box
                    key={index}
                    sx={{
                      mb: 3,
                      p: 2,
                      borderRadius: 1,
                      bgcolor: diff.type === 'same' ? '#f5f5f5' : 
                               diff.type === 'modified' ? '#fff3e0' :
                               diff.type === 'removed' ? '#ffebee' : '#f5f5f5',
                      border: '1px solid',
                      borderColor: diff.type === 'same' ? '#e0e0e0' :
                                   diff.type === 'modified' ? '#ff9800' :
                                   diff.type === 'removed' ? '#f44336' : '#e0e0e0'
                    }}
                  >
                    <Typography variant="subtitle2" color="primary" gutterBottom>
                      {item.article}
                    </Typography>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {item.content}
                    </Typography>
                  </Box>
                )
              })}
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper 
            elevation={3} 
            sx={{ 
              height: '600px', 
              overflow: 'auto',
              border: syncScroll ? '2px solid #dc004e' : 'none'
            }}
            ref={scrollRef2}
            onScroll={handleScroll(scrollRef2, scrollRef1)}
          >
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom color="secondary">
                {selectedV2}
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {v2Content.map((item, index) => {
                const v1Item = v1Content[index]
                const diff = v1Item ? getDifferences(v1Item.content, item.content) : { type: 'added' }
                
                return (
                  <Box
                    key={index}
                    sx={{
                      mb: 3,
                      p: 2,
                      borderRadius: 1,
                      bgcolor: diff.type === 'same' ? '#f5f5f5' :
                               diff.type === 'modified' ? '#fff3e0' :
                               diff.type === 'added' ? '#e8f5e9' : '#f5f5f5',
                      border: '1px solid',
                      borderColor: diff.type === 'same' ? '#e0e0e0' :
                                   diff.type === 'modified' ? '#ff9800' :
                                   diff.type === 'added' ? '#4caf50' : '#e0e0e0'
                    }}
                  >
                    <Typography variant="subtitle2" color="secondary" gutterBottom>
                      {item.article}
                    </Typography>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {item.content}
                    </Typography>
                  </Box>
                )
              })}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 2 }}>
        <Alert severity="info">
          <Typography variant="caption">
            <strong>Color Legend:</strong> 
            {' '}Gray = Same content | 
            {' '}Orange = Modified | 
            {' '}Green = Added in V2 | 
            {' '}Red = Removed in V2
          </Typography>
        </Alert>
      </Box>
    </Container>
  )
}
