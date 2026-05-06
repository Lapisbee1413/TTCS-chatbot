import { Container, Paper, Typography, Button, Box, Alert } from '@mui/material'
import { Link, isRouteErrorResponse, useRouteError } from 'react-router-dom'

export default function RouteErrorPage() {
  const error = useRouteError()

  const status = isRouteErrorResponse(error) ? error.status : 500
  const title = isRouteErrorResponse(error) && error.status === 404
    ? 'Page not found'
    : 'Unexpected application error'
  const message = isRouteErrorResponse(error)
    ? error.statusText || 'An unexpected routing error occurred'
    : error?.message || 'An unexpected error occurred'

  return (
    <Container maxWidth="md" sx={{ mt: 6 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          {status} — {title}
        </Typography>
        <Alert severity="error" sx={{ mb: 3 }}>
          {message}
        </Alert>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="contained" component={Link} to="/">
            Go to Home
          </Button>
          <Button variant="outlined" onClick={() => window.location.reload()}>
            Reload
          </Button>
        </Box>
      </Paper>
    </Container>
  )
}
