import { useState } from 'react'
import {
  Container, Paper, Typography, Button, TextField, Box,
  Alert, LinearProgress, Chip, List, ListItem, ListItemIcon,
  ListItemText, Divider,
} from '@mui/material'
import {
  CloudUpload, CheckCircle as CheckIcon, Warning as WarnIcon,
  Cancel as FailIcon, InsertDriveFile, VerifiedUser,
} from '@mui/icons-material'
import { uploadDocument } from '../api/client'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [sourceName, setSourceName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [qualityReject, setQualityReject] = useState(null)


  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
      setQualityReject(null)
      setResult(null)
      if (!sourceName) {
        setSourceName(selectedFile.name.replace(/\.[^/.]+$/, ''))
      }
    }
  }



  const handleUpload = async (forceUpload = false) => {
    if (!file) { setError('Vui lòng chọn file'); return }
    if (!file.name.match(/\.(pdf|docx)$/i)) { setError('Chỉ hỗ trợ file PDF và DOCX'); return }
    if (file.size > 10 * 1024 * 1024) { setError('Kích thước file phải nhỏ hơn 10MB'); return }

    setUploading(true); setError(null); setResult(null); setQualityReject(null)
    try {
      const response = await uploadDocument(file, sourceName || null, forceUpload)
      setResult(response); setFile(null); setSourceName('')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (detail && typeof detail === 'object' && detail.quality) {
        setQualityReject(detail)
      } else {
        setError(typeof detail === 'string' ? detail : detail?.message || err.message || 'Upload thất bại')
      }
    } finally { setUploading(false) }
  }

  const getQualityColor = (q) => q === 'HIGH' ? 'success' : q === 'MEDIUM' ? 'warning' : q === 'LOW' ? 'error' : 'default'
  const getQualityLabel = (q) => q === 'HIGH' ? 'Cao' : q === 'MEDIUM' ? 'Trung bình' : q === 'LOW' ? 'Thấp' : q
  const getCheckIcon = (s) => s >= 70 ? <CheckIcon color="success" fontSize="small" /> : s >= 40 ? <WarnIcon color="warning" fontSize="small" /> : <FailIcon color="error" fontSize="small" />
  const fmtSize = (b) => b < 1024 ? `${b} B` : b < 1048576 ? `${(b/1024).toFixed(1)} KB` : `${(b/1048576).toFixed(1)} MB`

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3, background: 'linear-gradient(135deg, #fafbfc 0%, #fff 100%)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <CloudUpload sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" sx={{ fontWeight: 600 }}>Tải tài liệu</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" paragraph>
          Tải lên tài liệu PDF hoặc DOCX. Tài liệu sẽ được tự động kiểm tra chất lượng trước khi đưa vào kho dữ liệu.
        </Typography>

        <Box sx={{ mt: 3 }}>
          {/* File Select Button */}
          <Button
            variant="outlined"
            component="label"
            startIcon={<CloudUpload />}
            disabled={uploading}
            fullWidth
            size="large"
            sx={{
              py: 1.5, borderRadius: 2, fontWeight: 600, fontSize: '1rem',
              textTransform: 'none', borderWidth: 2,
              '&:hover': { borderWidth: 2 },
            }}
          >
            Chọn file (PDF, DOCX)
            <input type="file" hidden accept=".pdf,.docx" onChange={handleFileChange} />
          </Button>

          {file && (
            <Alert
              icon={<InsertDriveFile sx={{ color: '#2e7d32' }} />}
              severity="success"
              sx={{ mt: 1.5, borderRadius: 2 }}
            >
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {file.name} ({fmtSize(file.size)})
              </Typography>
            </Alert>
          )}

          <TextField label="Tên nguồn (không bắt buộc)" variant="outlined" fullWidth value={sourceName}
            onChange={(e) => setSourceName(e.target.value)} sx={{ mt: 2.5 }} disabled={uploading} helperText="VD: HopDong_V1, PhuLuc_V2" />

          <Button variant="contained" startIcon={<CloudUpload />} onClick={() => handleUpload(false)}
            disabled={!file || uploading} fullWidth size="large"
            sx={{ mt: 2.5, py: 1.5, borderRadius: 2, fontWeight: 600, fontSize: '1rem', textTransform: 'none',
              background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
              '&:hover': { background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)' } }}>
            {uploading ? 'Đang tải lên & kiểm tra...' : 'Tải lên & Kiểm tra chất lượng'}
          </Button>

          {uploading && <LinearProgress sx={{ mt: 2, borderRadius: 1, height: 6 }} />}
          {error && <Alert severity="error" sx={{ mt: 2.5, borderRadius: 2 }}>{error}</Alert>}

          {/* Quality Rejection Card */}
          {qualityReject && (
            <Paper variant="outlined" sx={{ mt: 2.5, borderRadius: 2, borderColor: 'rgba(229,57,53,0.3)', overflow: 'hidden' }}>
              <Box sx={{ px: 2.5, py: 1.5, backgroundColor: 'rgba(229,57,53,0.06)', borderBottom: '1px solid rgba(229,57,53,0.15)', display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <FailIcon sx={{ color: '#e53935' }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#e53935', flex: 1 }}>Tài liệu bị từ chối</Typography>
                <Chip label={`${qualityReject.quality} (${qualityReject.score}/100)`} size="small" color="error" />
              </Box>
              <Box sx={{ px: 2.5, py: 2 }}>
                <Typography variant="body2" sx={{ mb: 1.5 }}>{qualityReject.message}</Typography>
                {qualityReject.checks && (<>
                  <Divider sx={{ mb: 1.5 }} />
                  <List dense disablePadding>
                    {qualityReject.checks.map((check, idx) => (
                      <ListItem key={idx} sx={{ py: 0.3, px: 0 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>{getCheckIcon(check.score)}</ListItemIcon>
                        <ListItemText primary={`${check.name}: ${check.score}/100`} secondary={check.reason}
                          primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }} secondaryTypographyProps={{ variant: 'caption' }} />
                      </ListItem>
                    ))}
                  </List>
                </>)}
                <Button variant="outlined" color="warning" size="small" startIcon={<WarnIcon />}
                  sx={{ mt: 1.5, borderRadius: 1.5, textTransform: 'none', fontWeight: 600 }}
                  onClick={() => handleUpload(true)} disabled={uploading}>
                  Bỏ qua kiểm tra và tải lên
                </Button>
              </Box>
            </Paper>
          )}

          {/* Success Card */}
          {result && (
            <Paper variant="outlined" sx={{ mt: 2.5, borderRadius: 2, overflow: 'hidden',
              borderColor: result.quality === 'MEDIUM' ? 'rgba(245,124,0,0.3)' : 'rgba(46,125,50,0.3)' }}>
              <Box sx={{ px: 2.5, py: 1.5, display: 'flex', alignItems: 'center', gap: 1.5,
                backgroundColor: result.quality === 'MEDIUM' ? 'rgba(245,124,0,0.06)' : 'rgba(46,125,50,0.06)',
                borderBottom: `1px solid ${result.quality === 'MEDIUM' ? 'rgba(245,124,0,0.15)' : 'rgba(46,125,50,0.15)'}` }}>
                <VerifiedUser sx={{ color: result.quality === 'MEDIUM' ? '#f57c00' : '#2e7d32' }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 600, flex: 1, color: result.quality === 'MEDIUM' ? '#f57c00' : '#2e7d32' }}>
                  {result.forced ? 'Tải lên thành công (bỏ qua kiểm tra)' : 'Tải lên thành công!'}
                </Typography>
                <Chip label={`${getQualityLabel(result.quality)} (${result.quality_score}/100)`} size="small" color={getQualityColor(result.quality)} />
              </Box>
              <Box sx={{ px: 2.5, py: 2 }}>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 2, mb: result.quality_summary ? 1.5 : 0 }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">Tên tài liệu</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{result.document_name}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">Tên nguồn</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{result.source_name}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">Số chunks</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{result.num_chunks}</Typography>
                  </Box>
                </Box>
                {result.quality_summary && <Typography variant="caption" color="text.secondary">{result.quality_summary}</Typography>}
              </Box>
            </Paper>
          )}
        </Box>
      </Paper>
    </Container>
  )
}
