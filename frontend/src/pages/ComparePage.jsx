import { useState, useEffect, useMemo } from 'react'
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
  Chip,
  Collapse,
  IconButton,
} from '@mui/material'
import {
  CompareArrows,
  DifferenceOutlined,
  PlaylistAddOutlined,
  CheckCircleOutline,
  SummarizeOutlined,
  ExpandMore,
  ExpandLess,
  WarningAmber,
} from '@mui/icons-material'
import { compareVersions, listDocuments } from '../api/client'

/**
 * Parse the raw comparison_report text into structured sections.
 * The LLM outputs sections like:
 *   **1. ĐIỂM KHÁC BIỆT**
 *   **2. NỘI DUNG MỚI THÊM/BỎ ĐI**
 *   **3. ĐIỂM GIỐNG NHAU**
 *   **4. TÓM TẮT V1 (...)** 
 *   **5. TÓM TẮT V2 (...)**
 */
function parseComparisonReport(report) {
  if (!report) return []

  // Define section patterns — order matters for matching
  const sectionDefs = [
    {
      id: 'differences',
      pattern: /\*{0,2}\s*1\.\s*ĐIỂM KHÁC BIỆT\s*\*{0,2}/i,
      label: 'Điểm khác biệt',
      icon: 'difference',
      color: '#e53935',
      bgColor: 'rgba(229, 57, 53, 0.06)',
      borderColor: 'rgba(229, 57, 53, 0.25)',
    },
    {
      id: 'added_removed',
      pattern: /\*{0,2}\s*2\.\s*NỘI DUNG MỚI THÊM\s*\/?\s*BỎ ĐI\s*\*{0,2}/i,
      label: 'Nội dung mới thêm / Bỏ đi',
      icon: 'playlist',
      color: '#f57c00',
      bgColor: 'rgba(245, 124, 0, 0.06)',
      borderColor: 'rgba(245, 124, 0, 0.25)',
    },
    {
      id: 'similarities',
      pattern: /\*{0,2}\s*3\.\s*ĐIỂM GIỐNG NHAU\s*\*{0,2}/i,
      label: 'Điểm giống nhau',
      icon: 'check',
      color: '#2e7d32',
      bgColor: 'rgba(46, 125, 50, 0.06)',
      borderColor: 'rgba(46, 125, 50, 0.25)',
    },
    {
      id: 'summary_v1',
      pattern: /\*{0,2}\s*4\.\s*TÓM TẮT\s*V1\s*(?:\([^)]*\))?\s*\*{0,2}/i,
      label: 'Tóm tắt V1',
      icon: 'summary',
      color: '#1565c0',
      bgColor: 'rgba(21, 101, 192, 0.06)',
      borderColor: 'rgba(21, 101, 192, 0.25)',
    },
    {
      id: 'summary_v2',
      pattern: /\*{0,2}\s*5\.\s*TÓM TẮT\s*V2\s*(?:\([^)]*\))?\s*\*{0,2}/i,
      label: 'Tóm tắt V2',
      icon: 'summary',
      color: '#7b1fa2',
      bgColor: 'rgba(123, 31, 162, 0.06)',
      borderColor: 'rgba(123, 31, 162, 0.25)',
    },
  ]

  // Find all section positions
  const sectionPositions = []
  for (const def of sectionDefs) {
    const match = report.match(def.pattern)
    if (match) {
      sectionPositions.push({
        ...def,
        matchStart: match.index,
        matchEnd: match.index + match[0].length,
        matchText: match[0],
      })
    }
  }

  // Sort by position in text
  sectionPositions.sort((a, b) => a.matchStart - b.matchStart)

  // Extract content for each section
  const sections = []
  for (let i = 0; i < sectionPositions.length; i++) {
    const current = sectionPositions[i]
    const next = sectionPositions[i + 1]

    const contentStart = current.matchEnd
    const contentEnd = next ? next.matchStart : report.length
    let content = report.substring(contentStart, contentEnd).trim()

    // Clean up markdown bold markers and leading/trailing whitespace
    content = content
      .replace(/^\s*\n/, '')  // remove leading newline
      .replace(/\n\s*$/, '')  // remove trailing whitespace

    sections.push({
      id: current.id,
      label: current.label,
      icon: current.icon,
      color: current.color,
      bgColor: current.bgColor,
      borderColor: current.borderColor,
      content,
    })
  }

  // If no sections were parsed, return the whole report as a single section
  if (sections.length === 0) {
    sections.push({
      id: 'full_report',
      label: 'Báo cáo so sánh',
      icon: 'summary',
      color: '#455a64',
      bgColor: 'rgba(69, 90, 100, 0.06)',
      borderColor: 'rgba(69, 90, 100, 0.25)',
      content: report,
    })
  }

  return sections
}

/**
 * Clean and render content lines with proper formatting.
 * Converts markdown-like bullet points to clean React elements.
 */
function ReportContent({ content, color }) {
  if (!content) return <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>Không có nội dung</Typography>

  const lines = content.split('\n')

  return (
    <Box sx={{ '& > *:not(:last-child)': { mb: 0.8 } }}>
      {lines.map((line, idx) => {
        const trimmed = line.trim()
        if (!trimmed) return null

        // Detect bullet lines: starts with -, *, •, or numbered
        const bulletMatch = trimmed.match(/^(\s*)([*\-•]|\d+\.)\s+(.*)$/)

        if (bulletMatch) {
          const bulletContent = bulletMatch[3]
          const isSubBullet = line.match(/^\s{2,}/)

          // Format quoted text (text in "..." quotes)
          const formattedContent = formatQuotedText(bulletContent, color)

          return (
            <Box
              key={idx}
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 1,
                pl: isSubBullet ? 3 : 1,
              }}
            >
              <Box
                sx={{
                  width: 6,
                  height: 6,
                  minWidth: 6,
                  borderRadius: '50%',
                  backgroundColor: color,
                  mt: '8px',
                  opacity: isSubBullet ? 0.5 : 0.8,
                }}
              />
              <Typography
                variant="body2"
                sx={{
                  lineHeight: 1.7,
                  color: 'text.primary',
                }}
              >
                {formattedContent}
              </Typography>
            </Box>
          )
        }

        // Regular text lines
        // Clean up markdown bold: **text** → render as bold
        const formattedLine = formatBoldText(trimmed)

        return (
          <Typography
            key={idx}
            variant="body2"
            sx={{
              lineHeight: 1.7,
              color: 'text.primary',
              pl: 1,
            }}
          >
            {formattedLine}
          </Typography>
        )
      })}
    </Box>
  )
}

/**
 * Format text with quoted parts highlighted
 */
function formatQuotedText(text, color) {
  // Match V1 = "..." → V2 = "..." pattern
  const parts = []
  let lastIndex = 0

  // Highlight quoted strings
  const quoteRegex = /"([^"]+)"/g
  let match

  while ((match = quoteRegex.exec(text)) !== null) {
    // Add text before quote
    if (match.index > lastIndex) {
      parts.push(
        <span key={`t-${lastIndex}`}>{formatBoldText(text.substring(lastIndex, match.index))}</span>
      )
    }
    // Add quoted text with highlight
    parts.push(
      <Box
        component="span"
        key={`q-${match.index}`}
        sx={{
          backgroundColor: `${color}14`,
          color: color,
          fontWeight: 600,
          px: 0.5,
          borderRadius: 0.5,
          fontSize: '0.85rem',
        }}
      >
        &ldquo;{match[1]}&rdquo;
      </Box>
    )
    lastIndex = match.index + match[0].length
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(
      <span key={`t-${lastIndex}`}>{formatBoldText(text.substring(lastIndex))}</span>
    )
  }

  return parts.length > 0 ? parts : formatBoldText(text)
}

/**
 * Format markdown bold (**text**) to React elements
 */
function formatBoldText(text) {
  if (typeof text !== 'string') return text

  const parts = []
  let lastIndex = 0
  const boldRegex = /\*\*([^*]+)\*\*/g
  let match

  while ((match = boldRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index))
    }
    parts.push(
      <strong key={`b-${match.index}`}>{match[1]}</strong>
    )
    lastIndex = match.index + match[0].length
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex))
  }

  return parts.length > 0 ? parts : text
}

/**
 * Get the icon component for a section
 */
function getSectionIcon(iconName) {
  switch (iconName) {
    case 'difference': return <DifferenceOutlined />
    case 'playlist': return <PlaylistAddOutlined />
    case 'check': return <CheckCircleOutline />
    case 'summary': return <SummarizeOutlined />
    default: return <SummarizeOutlined />
  }
}

/**
 * A single report section card
 */
function ReportSectionCard({ section, defaultExpanded = true }) {
  const [expanded, setExpanded] = useState(defaultExpanded)

  return (
    <Paper
      variant="outlined"
      sx={{
        overflow: 'hidden',
        borderColor: section.borderColor,
        borderWidth: 1,
        borderRadius: 2,
        transition: 'box-shadow 0.2s ease',
        '&:hover': {
          boxShadow: `0 2px 12px ${section.borderColor}`,
        },
      }}
    >
      {/* Section Header */}
      <Box
        onClick={() => setExpanded(!expanded)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          px: 2.5,
          py: 1.5,
          cursor: 'pointer',
          backgroundColor: section.bgColor,
          borderBottom: expanded ? `1px solid ${section.borderColor}` : 'none',
          userSelect: 'none',
          transition: 'background-color 0.2s ease',
          '&:hover': {
            backgroundColor: `${section.color}12`,
          },
        }}
      >
        <Box sx={{ color: section.color, display: 'flex', alignItems: 'center' }}>
          {getSectionIcon(section.icon)}
        </Box>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 600,
            color: section.color,
            flex: 1,
            fontSize: '0.95rem',
          }}
        >
          {section.label}
        </Typography>
        <IconButton size="small" sx={{ color: section.color }}>
          {expanded ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      </Box>

      {/* Section Content */}
      <Collapse in={expanded}>
        <Box sx={{ px: 2.5, py: 2 }}>
          <ReportContent content={section.content} color={section.color} />
        </Box>
      </Collapse>
    </Paper>
  )
}

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
      setError('Vui lòng điền đầy đủ thông tin')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await compareVersions(articleName, sourceV1, sourceV2)
      setResult(response)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'So sánh thất bại')
    } finally {
      setLoading(false)
    }
  }

  // Parse the report into sections
  const parsedSections = useMemo(() => {
    if (!result?.comparison_report) return []
    return parseComparisonReport(result.comparison_report)
  }, [result?.comparison_report])

  // Detect truncation warning
  const hasTruncationWarning = result?.comparison_report?.includes('⚠️')

  return (
    <Container maxWidth="lg">
      {/* Input Form */}
      <Paper
        elevation={3}
        sx={{
          p: 4,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #fafbfc 0%, #ffffff 100%)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <CompareArrows sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            So sánh phiên bản
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" paragraph>
          So sánh điều khoản cụ thể giữa hai phiên bản tài liệu pháp lý
        </Typography>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid size={12}>
            <TextField
              label="Tên điều khoản"
              variant="outlined"
              fullWidth
              value={articleName}
              onChange={(e) => setArticleName(e.target.value)}
              placeholder='VD: Điều 5'
              disabled={loading}
            />
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControl fullWidth>
              <InputLabel>Phiên bản 1</InputLabel>
              <Select
                value={sourceV1}
                onChange={(e) => setSourceV1(e.target.value)}
                label="Phiên bản 1"
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
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControl fullWidth>
              <InputLabel>Phiên bản 2</InputLabel>
              <Select
                value={sourceV2}
                onChange={(e) => setSourceV2(e.target.value)}
                label="Phiên bản 2"
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
          size="large"
          sx={{
            py: 1.5,
            borderRadius: 2,
            fontWeight: 600,
            fontSize: '1rem',
            textTransform: 'none',
            background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
            },
          }}
        >
          {loading ? 'Đang so sánh...' : 'So sánh'}
        </Button>
      </Paper>

      {/* Loading State */}
      {loading && (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4, gap: 2 }}>
          <CircularProgress size={40} />
          <Typography variant="body2" color="text.secondary">
            Đang phân tích và so sánh nội dung...
          </Typography>
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mt: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {result && (
        <Box sx={{ mt: 4 }}>
          {/* Success Banner */}
          <Alert
            severity="success"
            sx={{
              mb: 3,
              borderRadius: 2,
              '& .MuiAlert-message': { fontWeight: 500 },
            }}
          >
            So sánh hoàn tất — {articleName} giữa {result.v1_source} và {result.v2_source}
          </Alert>

          {/* Truncation Warning */}
          {hasTruncationWarning && (
            <Alert
              severity="warning"
              icon={<WarningAmber />}
              sx={{ mb: 3, borderRadius: 2 }}
            >
              Báo cáo có thể bị cắt ngắn. Vui lòng thử lại nếu kết quả chưa đầy đủ.
            </Alert>
          )}

          {/* Source Text Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Paper
                variant="outlined"
                sx={{
                  p: 2.5,
                  borderRadius: 2,
                  borderColor: 'rgba(21, 101, 192, 0.3)',
                  borderLeft: '4px solid #1565c0',
                  maxHeight: 300,
                  overflow: 'auto',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                  <Chip
                    label="V1"
                    size="small"
                    sx={{
                      backgroundColor: '#1565c0',
                      color: '#fff',
                      fontWeight: 700,
                      fontSize: '0.7rem',
                    }}
                  />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1565c0' }}>
                    {result.v1_source}
                  </Typography>
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    color: 'text.secondary',
                    lineHeight: 1.7,
                    fontSize: '0.85rem',
                  }}
                >
                  {result.v1_text || 'Không tìm thấy nội dung'}
                </Typography>
              </Paper>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <Paper
                variant="outlined"
                sx={{
                  p: 2.5,
                  borderRadius: 2,
                  borderColor: 'rgba(123, 31, 162, 0.3)',
                  borderLeft: '4px solid #7b1fa2',
                  maxHeight: 300,
                  overflow: 'auto',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                  <Chip
                    label="V2"
                    size="small"
                    sx={{
                      backgroundColor: '#7b1fa2',
                      color: '#fff',
                      fontWeight: 700,
                      fontSize: '0.7rem',
                    }}
                  />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#7b1fa2' }}>
                    {result.v2_source}
                  </Typography>
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    color: 'text.secondary',
                    lineHeight: 1.7,
                    fontSize: '0.85rem',
                  }}
                >
                  {result.v2_text || 'Không tìm thấy nội dung'}
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }}>
            <Chip
              label="BÁO CÁO SO SÁNH"
              size="small"
              sx={{
                fontWeight: 700,
                letterSpacing: 0.5,
                backgroundColor: '#f5f5f5',
                color: 'text.primary',
              }}
            />
          </Divider>

          {/* Parsed Report Sections */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {parsedSections.map((section) => (
              <ReportSectionCard
                key={section.id}
                section={section}
                defaultExpanded={true}
              />
            ))}
          </Box>

          {/* Citations */}
          {result.citations && result.citations.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                Nguồn trích dẫn:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {result.citations.map((cite, idx) => (
                  <Chip
                    key={idx}
                    label={`${cite.source} — ${cite.article_ref}`}
                    size="small"
                    variant="outlined"
                    sx={{ fontSize: '0.75rem' }}
                  />
                ))}
              </Box>
            </Box>
          )}
        </Box>
      )}
    </Container>
  )
}
