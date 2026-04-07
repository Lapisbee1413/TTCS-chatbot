import { Box, Typography, Button } from '@mui/material'
import { Inbox as InboxIcon } from '@mui/icons-material'

export default function EmptyState({ title, description, action, actionLabel }) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 4,
        textAlign: 'center',
      }}
    >
      <InboxIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
      <Typography variant="h6" color="text.secondary" gutterBottom>
        {title}
      </Typography>
      {description && (
        <Typography variant="body2" color="text.secondary" paragraph>
          {description}
        </Typography>
      )}
      {action && actionLabel && (
        <Button variant="contained" onClick={action} sx={{ mt: 2 }}>
          {actionLabel}
        </Button>
      )}
    </Box>
  )
}
