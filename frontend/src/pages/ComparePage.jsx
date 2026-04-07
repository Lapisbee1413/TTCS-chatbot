import { useState, useEffect } from 'react'
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material'
import { CompareArrows } from '@mui/icons-material'
import { compareVersions, listDocuments } from '../api/client'

export default function ComparePage() {
  const [documents, setDocuments] = useState([])
  const [articleName, setArticleName] = useState('')
  const [sourceV1, setSourceV1] = useState('')
  const [sourceV2, setSourceV2] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const response = await listDocuments()
      setDocuments(response.documents || [])
      
      if (response.documents && response.documents.length >= 2) {
        setSourceV1(response.documents[0].source)
        setSourceV2(response.documents[1].source)
      }
    } catch (err) {
      console.error('Failed to load documents:', err)
    }
  }

  const handleCompare = async () => {
    if (!articleName || !sourceV1 || !sourceV2) {
      setError('Please fill in all fields')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await compareVersions(articleName, sourceV1, sourceV2)
      setResult(response)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Comparison failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Compare Versions
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Compare specific articles between two document versions
        </Typography>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12}>
            <TextField
              label="Article Name"
              variant="outlined"
              fullWidth
              value={articleName}
              onChange={(e) => setArticleName(e.target.value)}
              placeholder="e.g., Điều 5"
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Version 1</InputLabel>
              <Select
                value={sourceV1}
                onChange={(e) => setSourceV1(e.target.value)}
                label="Version 1"
                disabled={loading}
              >
                {documents.map((doc) => (
                  <MenuItem key={doc.source} value={doc.source}>
                    {doc.source}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Version 2</InputLabel>
              <Select
                value={sourceV2}
                onChange={(e) => setSourceV2(e.target.value)}
                label="Version 2"
                disabled={loading}
              >
                {documents.map((doc) => (
                  <MenuItem key={doc.source} value={doc.source}>
                    {doc.source}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Button
          variant="contained"
          startIcon={<CompareArrows />}
          onClick={handleCompare}
          disabled={!articleName || !sourceV1 || !sourceV2 || loading}
          fullWidth
        >
          {loading ? 'Comparing...' : 'Compare'}
        </Button>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 3 }}>
            {error}
          </Alert>
        )}

        {result && (
          <Box sx={{ mt: 3 }}>
            <Alert severity="success" sx={{ mb: 3 }}>
              Comparison completed successfully
            </Alert>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="h6" color="primary" gutterBottom>
                    {result.v1_source}
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {result.v1_text || 'No content found'}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="h6" color="secondary" gutterBottom>
                    {result.v2_source}
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {result.v2_text || 'No content found'}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Paper variant="outlined" sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Comparison Report
              </Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {result.comparison_report}
              </Typography>
            </Paper>
          </Box>
        )}
      </Paper>
    </Container>
  )
}
