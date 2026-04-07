import { useState } from 'react'
import {
  Container,
  Paper,
  Typography,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress,
  LinearProgress,
} from '@mui/material'
import { CloudUpload } from '@mui/icons-material'
import { uploadDocument } from '../api/client'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [sourceName, setSourceName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
      // Auto-fill source name from filename
      if (!sourceName) {
        setSourceName(selectedFile.name.replace(/\.[^/.]+$/, ''))
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    // Validate file type
    if (!file.name.match(/\.(pdf|docx)$/i)) {
      setError('Only PDF and DOCX files are supported')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setUploading(true)
    setError(null)
    setResult(null)

    try {
      const response = await uploadDocument(file, sourceName || null)
      setResult(response)
      setFile(null)
      setSourceName('')
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Upload Document
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Upload a PDF or DOCX legal document to add it to the knowledge base
        </Typography>

        <Box sx={{ mt: 3 }}>
          <Button
            variant="contained"
            component="label"
            startIcon={<CloudUpload />}
            disabled={uploading}
            fullWidth
          >
            Select File
            <input type="file" hidden accept=".pdf,.docx" onChange={handleFileChange} />
          </Button>

          {file && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </Alert>
          )}

          <TextField
            label="Source Name (optional)"
            variant="outlined"
            fullWidth
            value={sourceName}
            onChange={(e) => setSourceName(e.target.value)}
            sx={{ mt: 2 }}
            disabled={uploading}
            helperText="e.g., HopDong_V1, PhuLuc_V2"
          />

          <Button
            variant="contained"
            color="primary"
            onClick={handleUpload}
            disabled={!file || uploading}
            fullWidth
            sx={{ mt: 2 }}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </Button>

          {uploading && <LinearProgress sx={{ mt: 2 }} />}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {result && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="body1">
                <strong>Success!</strong> {result.message}
              </Typography>
              <Typography variant="body2">
                Document: {result.document_name}
                <br />
                Source: {result.source_name}
                <br />
                Chunks created: {result.num_chunks}
              </Typography>
            </Alert>
          )}
        </Box>
      </Paper>
    </Container>
  )
}
