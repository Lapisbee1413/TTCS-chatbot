import { useState, useEffect } from 'react'
import {
  Container,
  Paper,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Collapse,
  Tooltip,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Description as DocIcon,
} from '@mui/icons-material'
import { listDocuments, getDocumentContent, deleteDocument } from '../api/client'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [deleteDialog, setDeleteDialog] = useState({ open: false, source: null })
  const [deleting, setDeleting] = useState(false)
  const [expandedDoc, setExpandedDoc] = useState(null)
  const [docContent, setDocContent] = useState({})
  const [contentLoading, setContentLoading] = useState(null)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await listDocuments()
      setDocuments(response.documents || [])
    } catch (err) {
      setError(err.message || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteClick = (source) => {
    setDeleteDialog({ open: true, source })
  }

  const handleDeleteConfirm = async () => {
    const source = deleteDialog.source
    setDeleteDialog({ open: false, source: null })
    setDeleting(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await deleteDocument(source)
      setSuccess(result.message)
      // Refresh document list
      await loadDocuments()
      // Clear expanded content if this doc was expanded
      if (expandedDoc === source) {
        setExpandedDoc(null)
      }
      delete docContent[source]
    } catch (err) {
      setError(err.message || 'Failed to delete document')
    } finally {
      setDeleting(false)
    }
  }

  const handleExpand = async (source) => {
    if (expandedDoc === source) {
      setExpandedDoc(null)
      return
    }

    setExpandedDoc(source)

    // Load content if not cached
    if (!docContent[source]) {
      setContentLoading(source)
      try {
        const response = await getDocumentContent(source)
        setDocContent((prev) => ({ ...prev, [source]: response.articles || [] }))
      } catch (err) {
        console.error(`Error loading content for ${source}:`, err)
        setDocContent((prev) => ({
          ...prev,
          [source]: [{ article: 'Error', content: `Không thể load nội dung: ${err.message}` }],
        }))
      } finally {
        setContentLoading(null)
      }
    }
  }

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              Documents
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Manage uploaded documents in the knowledge base
            </Typography>
          </Box>
          <Tooltip title="Refresh">
            <IconButton onClick={loadDocuments} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        {documents.length === 0 ? (
          <Alert severity="info">
            No documents uploaded yet. Go to Upload page to add documents.
          </Alert>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell width="40px" />
                  <TableCell><strong>Source Name</strong></TableCell>
                  <TableCell align="center"><strong>Chunks</strong></TableCell>
                  <TableCell><strong>Sample Articles</strong></TableCell>
                  <TableCell align="center"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {documents.map((doc) => (
                  <>
                    <TableRow
                      key={doc.source}
                      hover
                      sx={{ cursor: 'pointer', '&:hover': { bgcolor: '#f5f5f5' } }}
                    >
                      <TableCell>
                        <IconButton size="small" onClick={() => handleExpand(doc.source)}>
                          {expandedDoc === doc.source ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </TableCell>
                      <TableCell onClick={() => handleExpand(doc.source)}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <DocIcon color="primary" fontSize="small" />
                          <Typography variant="body1" fontWeight={500}>
                            {doc.source}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Chip label={doc.num_chunks} size="small" color="primary" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {doc.sample_articles.map((article, idx) => (
                            <Chip key={idx} label={article} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="Delete document">
                          <IconButton
                            color="error"
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteClick(doc.source)
                            }}
                            disabled={deleting}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>

                    {/* Expanded content row */}
                    <TableRow key={`${doc.source}-content`}>
                      <TableCell colSpan={5} sx={{ py: 0, border: expandedDoc === doc.source ? undefined : 'none' }}>
                        <Collapse in={expandedDoc === doc.source} timeout="auto" unmountOnExit>
                          <Box sx={{ p: 2, bgcolor: '#fafafa', borderRadius: 1, my: 1 }}>
                            <Typography variant="subtitle2" gutterBottom color="primary">
                              Document Content — {doc.source}
                            </Typography>

                            {contentLoading === doc.source ? (
                              <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                                <CircularProgress size={24} />
                              </Box>
                            ) : (
                              (docContent[doc.source] || []).map((item, idx) => (
                                <Paper key={idx} variant="outlined" sx={{ p: 2, mb: 1 }}>
                                  <Typography variant="subtitle2" color="secondary" gutterBottom>
                                    {item.article}
                                  </Typography>
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      whiteSpace: 'pre-wrap',
                                      maxHeight: '200px',
                                      overflow: 'auto',
                                    }}
                                  >
                                    {item.content}
                                  </Typography>
                                </Paper>
                              ))
                            )}
                          </Box>
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  </>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Total: {documents.length} document(s), {documents.reduce((sum, d) => sum + d.num_chunks, 0)} chunks
          </Typography>
        </Box>
      </Paper>

      {/* Delete confirmation dialog */}
      <Dialog open={deleteDialog.open} onClose={() => setDeleteDialog({ open: false, source: null })}>
        <DialogTitle>Delete Document</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete <strong>{deleteDialog.source}</strong>? This will remove all
            chunks from the knowledge base. This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, source: null })}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
