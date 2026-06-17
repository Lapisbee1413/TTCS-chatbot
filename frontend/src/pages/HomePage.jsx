import { Container, Typography, Paper, Box, Grid, Card, CardContent, Chip } from '@mui/material'
import {
  Upload,
  Chat,
  CompareArrows,
  ViewWeek,
  Folder,
  AutoAwesome,
  ArrowForward,
} from '@mui/icons-material'
import { Link } from 'react-router-dom'

const features = [
  {
    title: 'Tải tài liệu',
    description: 'Tải lên tài liệu PDF hoặc DOCX vào kho dữ liệu, tự động kiểm tra chất lượng',
    icon: <Upload />,
    path: '/upload',
    color: '#1565c0',
    gradient: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
    bgColor: 'rgba(21, 101, 192, 0.08)',
  },
  {
    title: 'Hỏi đáp AI',
    description: 'Đặt câu hỏi và nhận câu trả lời kèm trích dẫn từ tài liệu pháp lý',
    icon: <Chat />,
    path: '/chat',
    color: '#2e7d32',
    gradient: 'linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%)',
    bgColor: 'rgba(46, 125, 50, 0.08)',
  },
  {
    title: 'Xem song song',
    description: 'Xem song song hai phiên bản tài liệu với đồng bộ cuộn trang',
    icon: <ViewWeek />,
    path: '/parallel',
    color: '#e65100',
    gradient: 'linear-gradient(135deg, #e65100 0%, #bf360c 100%)',
    bgColor: 'rgba(230, 81, 0, 0.08)',
  },
  {
    title: 'So sánh phiên bản',
    description: 'So sánh điều khoản cụ thể giữa hai phiên bản, phân tích khác biệt chi tiết',
    icon: <CompareArrows />,
    path: '/compare',
    color: '#7b1fa2',
    gradient: 'linear-gradient(135deg, #7b1fa2 0%, #4a148c 100%)',
    bgColor: 'rgba(123, 31, 162, 0.08)',
  },
  {
    title: 'Quản lý tài liệu',
    description: 'Xem, quản lý và xoá các tài liệu đã tải lên trong kho dữ liệu',
    icon: <Folder />,
    path: '/documents',
    color: '#455a64',
    gradient: 'linear-gradient(135deg, #455a64 0%, #263238 100%)',
    bgColor: 'rgba(69, 90, 100, 0.08)',
  },
]

export default function HomePage() {
  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, md: 5 },
          mb: 4,
          borderRadius: 4,
          background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 50%, #1a237e 100%)',
          color: '#fff',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Decorative circles */}
        <Box
          sx={{
            position: 'absolute',
            top: -60,
            right: -60,
            width: 200,
            height: 200,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.06)',
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: -40,
            right: 80,
            width: 120,
            height: 120,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.04)',
          }}
        />

        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
            <AutoAwesome sx={{ fontSize: 28, opacity: 0.9 }} />
            <Chip
              label="RAG + Local LLM"
              size="small"
              sx={{
                backgroundColor: 'rgba(255,255,255,0.15)',
                color: '#fff',
                fontWeight: 600,
                fontSize: '0.75rem',
                backdropFilter: 'blur(10px)',
              }}
            />
          </Box>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              mb: 1.5,
              fontSize: { xs: '1.8rem', md: '2.5rem' },
              lineHeight: 1.2,
            }}
          >
            Chatbot phân tích
            <br />
            tài liệu pháp lý
          </Typography>
          <Typography
            variant="body1"
            sx={{
              opacity: 0.85,
              maxWidth: 520,
              lineHeight: 1.7,
              fontSize: '1rem',
            }}
          >
            Hệ thống AI hỗ trợ phân tích, so sánh và tra cứu tài liệu pháp lý
            với cơ chế RAG (Retrieval-Augmented Generation) và mô hình ngôn ngữ chạy cục bộ.
          </Typography>
        </Box>
      </Paper>

      {/* Feature Cards */}
      <Grid container spacing={2.5}>
        {features.map((feature) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={feature.title}>
            <Card
              component={Link}
              to={feature.path}
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                textDecoration: 'none',
                borderRadius: 3,
                border: '1px solid',
                borderColor: 'rgba(0,0,0,0.08)',
                boxShadow: 'none',
                transition: 'all 0.25s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: `0 8px 24px ${feature.color}20`,
                  borderColor: `${feature.color}40`,
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1, p: 3 }}>
                {/* Icon */}
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: feature.gradient,
                    color: '#fff',
                    mb: 2,
                    '& .MuiSvgIcon-root': { fontSize: 24 },
                  }}
                >
                  {feature.icon}
                </Box>

                {/* Title */}
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 600,
                    fontSize: '1.05rem',
                    mb: 0.8,
                    color: 'text.primary',
                  }}
                >
                  {feature.title}
                </Typography>

                {/* Description */}
                <Typography
                  variant="body2"
                  sx={{
                    color: 'text.secondary',
                    lineHeight: 1.6,
                    fontSize: '0.85rem',
                  }}
                >
                  {feature.description}
                </Typography>
              </CardContent>

              {/* Footer arrow */}
              <Box
                sx={{
                  px: 3,
                  pb: 2,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  color: feature.color,
                  opacity: 0.7,
                  transition: 'opacity 0.2s',
                  '.MuiCard-root:hover &': { opacity: 1 },
                }}
              >
                <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '0.8rem' }}>
                  Mở
                </Typography>
                <ArrowForward sx={{ fontSize: 14 }} />
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  )
}
