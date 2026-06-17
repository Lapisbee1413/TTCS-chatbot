import { useState, useEffect, useRef } from 'react'
import {
  Container, Paper, Typography, Box, Select, MenuItem, FormControl,
  InputLabel, Alert, CircularProgress, Switch, FormControlLabel,
  Divider, Chip,
} from '@mui/material'
import { ViewWeek, SyncAlt } from '@mui/icons-material'
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

  useEffect(() => { loadDocuments() }, [])
  useEffect(() => { if (selectedV1) loadDocumentContent(selectedV1, setV1Content) }, [selectedV1])
  useEffect(() => { if (selectedV2) loadDocumentContent(selectedV2, setV2Content) }, [selectedV2])

  const loadDocuments = async () => {
    try {
      const response = await listDocuments()
      setDocuments(response.documents || [])
      if (response.documents && response.documents.length >= 2) {
        setSelectedV1(response.documents[0].source)
        setSelectedV2(response.documents[1].source)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Không thể tải danh sách tài liệu')
    } finally { setLoading(false) }
  }

  const loadDocumentContent = async (source, setContent) => {
    try {
      const response = await getDocumentContent(source)
      setContent(response.articles || [])
    } catch (err) {
      console.error(`Error loading content for ${source}:`, err)
      setContent([{ article: 'Lỗi', content: `Không thể tải nội dung: ${err.message}` }])
    }
  }

  const handleScroll = (sourceRef, targetRef) => (event) => {
    if (!syncScroll || isScrolling.current) return
    isScrolling.current = true
    const source = event.target
    const pct = source.scrollTop / (source.scrollHeight - source.clientHeight)
    if (targetRef.current) {
      targetRef.current.scrollTop = pct * (targetRef.current.scrollHeight - targetRef.current.clientHeight)
    }
    setTimeout(() => { isScrolling.current = false }, 50)
  }

  const getDiffType = (text1, text2) => {
    if (text1 === text2) return 'same'
    if (!text1) return 'added'
    if (!text2) return 'removed'
    return 'modified'
  }

  const diffStyles = {
    same: {
      bg: '#f8f9fa', border: 'rgba(0,0,0,0.06)',
      label: 'Giống nhau', labelColor: '#78909c', labelBg: 'rgba(120,144,156,0.08)',
    },
    modified: {
      bg: 'rgba(245,124,0,0.04)', border: 'rgba(245,124,0,0.25)',
      label: 'Thay đổi', labelColor: '#e65100', labelBg: 'rgba(245,124,0,0.08)',
    },
    added: {
      bg: 'rgba(46,125,50,0.04)', border: 'rgba(46,125,50,0.25)',
      label: 'Mới thêm', labelColor: '#2e7d32', labelBg: 'rgba(46,125,50,0.08)',
    },
    removed: {
      bg: 'rgba(229,57,53,0.04)', border: 'rgba(229,57,53,0.25)',
      label: 'Đã xoá', labelColor: '#c62828', labelBg: 'rgba(229,57,53,0.08)',
    },
  }

  if (loading) {
    return (
      <Container><Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 6, gap: 2 }}>
        <CircularProgress size={40} />
        <Typography variant="body2" color="text.secondary">Đang tải danh sách tài liệu...</Typography>
      </Box></Container>
    )
  }

  if (error) {
    return <Container><Alert severity="error" sx={{ borderRadius: 2 }}>{error}</Alert></Container>
  }

  if (documents.length < 2) {
    return (
      <Container>
        <Alert severity="warning" sx={{ borderRadius: 2 }}>
          Cần ít nhất 2 tài liệu để sử dụng chế độ xem song song. Vui lòng tải lên tài liệu trước.
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 3, borderRadius: 3, background: 'linear-gradient(135deg, #fafbfc 0%, #fff 100%)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <ViewWeek sx={{ fontSize: 32, color: '#e65100' }} />
          <Typography variant="h4" sx={{ fontWeight: 600 }}>Xem song song</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" paragraph>
          Xem nội dung hai phiên bản tài liệu bên cạnh nhau với đồng bộ cuộn trang
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr auto 1fr' }, gap: 2, alignItems: 'center' }}>
          <FormControl fullWidth>
            <InputLabel>Phiên bản 1</InputLabel>
            <Select value={selectedV1} onChange={(e) => setSelectedV1(e.target.value)} label="Phiên bản 1">
              {documents.map((doc) => (
                <MenuItem key={doc.source} value={doc.source}>{doc.source} ({doc.num_chunks} chunks)</MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
            <SyncAlt sx={{ color: syncScroll ? '#1976d2' : 'text.disabled', fontSize: 20 }} />
            <FormControlLabel
              control={<Switch checked={syncScroll} onChange={(e) => setSyncScroll(e.target.checked)} size="small" />}
              label={<Typography variant="caption" sx={{ fontWeight: 500 }}>Đồng bộ cuộn</Typography>}
            />
          </Box>

          <FormControl fullWidth>
            <InputLabel>Phiên bản 2</InputLabel>
            <Select value={selectedV2} onChange={(e) => setSelectedV2(e.target.value)} label="Phiên bản 2">
              {documents.map((doc) => (
                <MenuItem key={doc.source} value={doc.source}>{doc.source} ({doc.num_chunks} chunks)</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Side-by-side Panels */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 2 }}>
        {/* V1 Panel */}
        <Paper
          elevation={2}
          sx={{
            height: '600px', overflow: 'auto', borderRadius: 3,
            border: '2px solid',
            borderColor: syncScroll ? 'rgba(21,101,192,0.3)' : 'transparent',
            transition: 'border-color 0.3s ease',
          }}
          ref={scrollRef1}
          onScroll={handleScroll(scrollRef1, scrollRef2)}
        >
          {/* Panel Header */}
          <Box sx={{
            position: 'sticky', top: 0, zIndex: 1, px: 2.5, py: 1.5,
            backgroundColor: 'rgba(21,101,192,0.06)',
            borderBottom: '1px solid rgba(21,101,192,0.15)',
            display: 'flex', alignItems: 'center', gap: 1,
            backdropFilter: 'blur(8px)',
          }}>
            <Chip label="V1" size="small" sx={{ backgroundColor: '#1565c0', color: '#fff', fontWeight: 700, fontSize: '0.7rem' }} />
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1565c0' }}>{selectedV1}</Typography>
            <Chip label={`${v1Content.length} điều`} size="small" variant="outlined" sx={{ ml: 'auto', fontSize: '0.7rem' }} />
          </Box>

          <Box sx={{ p: 2.5 }}>
            {v1Content.map((item, index) => {
              const v2Item = v2Content[index]
              const diff = v2Item ? getDiffType(item.content, v2Item.content) : 'removed'
              const style = diffStyles[diff]

              return (
                <Box key={index} sx={{
                  mb: 2, p: 2, borderRadius: 2,
                  backgroundColor: style.bg,
                  border: '1px solid', borderColor: style.border,
                  transition: 'box-shadow 0.2s ease',
                  '&:hover': { boxShadow: `0 2px 8px ${style.border}` },
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1565c0' }}>{item.article}</Typography>
                    {diff !== 'same' && (
                      <Chip label={style.label} size="small"
                        sx={{ fontSize: '0.65rem', height: 20, fontWeight: 600, color: style.labelColor, backgroundColor: style.labelBg }} />
                    )}
                  </Box>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7, color: 'text.secondary', fontSize: '0.85rem' }}>
                    {item.content}
                  </Typography>
                </Box>
              )
            })}
          </Box>
        </Paper>

        {/* V2 Panel */}
        <Paper
          elevation={2}
          sx={{
            height: '600px', overflow: 'auto', borderRadius: 3,
            border: '2px solid',
            borderColor: syncScroll ? 'rgba(123,31,162,0.3)' : 'transparent',
            transition: 'border-color 0.3s ease',
          }}
          ref={scrollRef2}
          onScroll={handleScroll(scrollRef2, scrollRef1)}
        >
          {/* Panel Header */}
          <Box sx={{
            position: 'sticky', top: 0, zIndex: 1, px: 2.5, py: 1.5,
            backgroundColor: 'rgba(123,31,162,0.06)',
            borderBottom: '1px solid rgba(123,31,162,0.15)',
            display: 'flex', alignItems: 'center', gap: 1,
            backdropFilter: 'blur(8px)',
          }}>
            <Chip label="V2" size="small" sx={{ backgroundColor: '#7b1fa2', color: '#fff', fontWeight: 700, fontSize: '0.7rem' }} />
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#7b1fa2' }}>{selectedV2}</Typography>
            <Chip label={`${v2Content.length} điều`} size="small" variant="outlined" sx={{ ml: 'auto', fontSize: '0.7rem' }} />
          </Box>

          <Box sx={{ p: 2.5 }}>
            {v2Content.map((item, index) => {
              const v1Item = v1Content[index]
              const diff = v1Item ? getDiffType(v1Item.content, item.content) : 'added'
              const style = diffStyles[diff]

              return (
                <Box key={index} sx={{
                  mb: 2, p: 2, borderRadius: 2,
                  backgroundColor: style.bg,
                  border: '1px solid', borderColor: style.border,
                  transition: 'box-shadow 0.2s ease',
                  '&:hover': { boxShadow: `0 2px 8px ${style.border}` },
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#7b1fa2' }}>{item.article}</Typography>
                    {diff !== 'same' && (
                      <Chip label={style.label} size="small"
                        sx={{ fontSize: '0.65rem', height: 20, fontWeight: 600, color: style.labelColor, backgroundColor: style.labelBg }} />
                    )}
                  </Box>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7, color: 'text.secondary', fontSize: '0.85rem' }}>
                    {item.content}
                  </Typography>
                </Box>
              )
            })}
          </Box>
        </Paper>
      </Box>

      {/* Legend */}
      <Paper variant="outlined" sx={{ mt: 2.5, px: 2.5, py: 1.5, borderRadius: 2, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.primary' }}>Chú thích:</Typography>
        {Object.entries(diffStyles).map(([key, style]) => (
          <Box key={key} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 12, height: 12, borderRadius: 0.5, backgroundColor: style.labelBg, border: `1px solid ${style.border}` }} />
            <Typography variant="caption" sx={{ color: style.labelColor, fontWeight: 500 }}>{style.label}</Typography>
          </Box>
        ))}
      </Paper>
    </Container>
  )
}
