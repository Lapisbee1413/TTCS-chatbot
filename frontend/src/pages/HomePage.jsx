import { Container, Typography, Paper, Box, Grid, Card, CardContent } from '@mui/material'
import { Upload, Chat, CompareArrows, ViewWeek } from '@mui/icons-material'
import { Link } from 'react-router-dom'

const features = [
  {
    title: 'Upload Documents',
    description: 'Upload PDF or DOCX legal documents to the knowledge base',
    icon: <Upload sx={{ fontSize: 60 }} />,
    path: '/upload',
  },
  {
    title: 'Chat & Query',
    description: 'Ask questions and get answers with citations',
    icon: <Chat sx={{ fontSize: 60 }} />,
    path: '/chat',
  },
  {
    title: 'Parallel View',
    description: 'View two document versions side-by-side',
    icon: <ViewWeek sx={{ fontSize: 60 }} />,
    path: '/parallel',
  },
  {
    title: 'Compare Versions',
    description: 'Compare specific articles between versions',
    icon: <CompareArrows sx={{ fontSize: 60 }} />,
    path: '/compare',
  },
]

export default function HomePage() {
  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          Legal Document RAG Chatbot
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          An AI-powered chatbot for legal document analysis with citation support.
          Upload documents, ask questions, and compare versions with evidence-based answers.
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        {features.map((feature) => (
          <Grid item xs={12} sm={6} md={3} key={feature.title}>
            <Card
              component={Link}
              to={feature.path}
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                textDecoration: 'none',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'scale(1.05)' },
              }}
            >
              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <Box sx={{ color: 'primary.main', mb: 2 }}>{feature.icon}</Box>
                <Typography variant="h6" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  )
}
