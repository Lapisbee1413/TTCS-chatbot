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
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import {
  CloudUpload,
  CheckCircle as CheckIcon,
  Warning as WarnIcon,
  Cancel as FailIcon,
} from '@mui/icons-material'
import { uploadDocument } from '../api/client'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [sourceName, setSourceName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [qualityReject, setQualityReject] = useState(null) // Validation rejection details

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
      setQualityReject(null)
      setResult(null)
      // Auto-fill source name from filename
      if (!sourceName) {
        setSourceName(selectedFile.name.replace(/\.[^/.]+$/, ''))
      }
    }
  }

  const handleUpload = async (forceUpload = false) => {
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
    setQualityReject(null)

    try {
      const response = await uploadDocument(file, sourceName || null, forceUpload)
      setResult(response)
      setFile(null)
      setSourceName('')
    } catch (err) {
      // Check if this is a quality validation rejection (422)
      const detail = err.response?.data?.detail
      if (detail && typeof detail === 'object' && detail.quality) {
        setQualityReject(detail)
      } else {
        setError(typeof detail === 'string' ? detail : detail?.message || err.message || 'Upload failed')
      }
    } finally {
      setUploading(false)
    }
  }

  const getQualityColor = (quality) => {
    switch (quality) {
      case 'HIGH': return 'success'
      case 'MEDIUM': return 'warning'
      case 'LOW': return 'error'
      default: return 'default'
    }
  }

  const getCheckIcon = (score) => {
    if (score >= 70) return <CheckIcon color="success" fontSize="small" />
    if (score >= 40) return <WarnIcon color="warning" fontSize="small" />
    return <FailIcon color="error" fontSize="small" />
  }

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Upload Document
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Upload a PDF or DOCX legal document. Documents are automatically validated for quality before being added to the knowledge base.
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
            onClick={() => handleUpload(false)}
            disabled={!file || uploading}
            fullWidth
            sx={{ mt: 2 }}
          >
            {uploading ? 'Uploading & Validating...' : 'Upload & Validate'}
          </Button>

          {uploading && <LinearProgress sx={{ mt: 2 }} />}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {/* Quality Rejection Alert */}
          {qualityReject && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <Typography variant="body1" gutterBottom>
                <strong>❌ Tài liệu bị từ chối</strong> — Chất lượng{' '}
                <Chip
                  label={`${qualityReject.quality} (${qualityReject.score}/100)`}
                  color="error"
                  size="small"
                />
              </Typography>
              <Typography variant="body2" gutterBottom>
                {qualityReject.message}
              </Typography>

              {qualityReject.checks && (
                <List dense sx={{ mt: 1 }}>
                  {qualityReject.checks.map((check, idx) => (
                    <ListItem key={idx} sx={{ py: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        {getCheckIcon(check.score)}
                      </ListItemIcon>
                      <ListItemText
                        primary={`${check.name}: ${check.score}/100`}
                        secondary={check.reason}
                        primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
                        secondaryTypographyProps={{ variant: 'caption' }}
                      />
                    </ListItem>
                  ))}
                </List>
              )}

              <Button
                variant="outlined"
                color="warning"
                size="small"
                sx={{ mt: 1 }}
                onClick={() => handleUpload(true)}
                disabled={uploading}
              >
                ⚠️ Force Upload (bỏ qua kiểm tra)
              </Button>
            </Alert>
          )}

          {/* Success Result */}
          {result && (
            <Alert
              severity={result.quality === 'MEDIUM' ? 'warning' : 'success'}
              sx={{ mt: 2 }}
            >
              <Typography variant="body1">
                <strong>{result.forced ? '⚠️ Upload thành công (forced)' : '✅ Upload thành công!'}</strong>{' '}
                {result.message}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Document: {result.document_name}
                <br />
                Source: {result.source_name}
                <br />
                Chunks created: {result.num_chunks}
                <br />
                Quality:{' '}
                <Chip
                  label={`${result.quality} (${result.quality_score}/100)`}
                  color={getQualityColor(result.quality)}
                  size="small"
                />
              </Typography>
              {result.quality_summary && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {result.quality_summary}
                </Typography>
              )}
            </Alert>
          )}
        </Box>
      </Paper>
    </Container>
  )
}

