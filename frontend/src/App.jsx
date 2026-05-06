import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import ErrorBoundary from './components/ErrorBoundary'
import RouteErrorPage from './components/RouteErrorPage'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import UploadPage from './pages/UploadPage'
import ChatPage from './pages/ChatPage'
import ParallelViewPage from './pages/ParallelViewPage'
import ComparePage from './pages/ComparePage'
import DocumentsPage from './pages/DocumentsPage'

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
})

// Define routes
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <RouteErrorPage />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'upload',
        element: <UploadPage />,
      },
      {
        path: 'chat',
        element: <ChatPage />,
      },
      {
        path: 'parallel',
        element: <ParallelViewPage />,
      },
      {
        path: 'compare',
        element: <ComparePage />,
      },
      {
        path: 'documents',
        element: <DocumentsPage />,
      },
    ],
  },
])

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <RouterProvider router={router} />
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App
