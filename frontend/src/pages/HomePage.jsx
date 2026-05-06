import { Container, Typography, Paper, Box, Grid, Card, CardContent } from '@mui/material'
import { Upload, Chat, CompareArrows, ViewWeek } from '@mui/icons-material'
import { Link } from 'react-router-dom'

const features = [
  {
    title: 'Upload Documents',
    description: 'Tải lên tài liệu PDF hoặc DOCX vào kho tài liệu',
    icon: <Upload sx={{ fontSize: 60 }} />,
    path: '/upload',
  },
  {
    title: 'Chat & Query',
    description: 'Đặt câu hỏi và nhận câu trả lời kèm trích dẫn',
    icon: <Chat sx={{ fontSize: 60 }} />,
    path: '/chat',
  },
  {
    title: 'Parallel View',
    description: 'Xem song song hai phiên bản tài liệu',
    icon: <ViewWeek sx={{ fontSize: 60 }} />,
    path: '/parallel',
  },
  {
    title: 'Compare Versions',
    description: 'So sánh các điều khoản cụ thể giữa hai phiên bản',
    icon: <CompareArrows sx={{ fontSize: 60 }} />,
    path: '/compare',
  },
]

export default function HomePage() {
  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          RAG + Local LLM Chatbot
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Chatbot AI hỗ trợ phân tích tài liệu với cơ chế RAG và mô hình LLM chạy local.
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
