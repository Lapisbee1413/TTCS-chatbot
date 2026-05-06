import { Outlet } from 'react-router-dom'
import {
  AppBar,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from '@mui/material'
import {
  Home as HomeIcon,
  Upload as UploadIcon,
  Chat as ChatIcon,
  CompareArrows as CompareIcon,
  ViewWeek as ParallelIcon,
  Folder as FolderIcon,
} from '@mui/icons-material'
import { Link, useLocation } from 'react-router-dom'

const drawerWidth = 240

const menuItems = [
  { text: 'Home', path: '/', icon: <HomeIcon /> },
  { text: 'Upload', path: '/upload', icon: <UploadIcon /> },
  { text: 'Chat', path: '/chat', icon: <ChatIcon /> },
  { text: 'Parallel View', path: '/parallel', icon: <ParallelIcon /> },
  { text: 'Compare', path: '/compare', icon: <CompareIcon /> },
  { text: 'Documents', path: '/documents', icon: <FolderIcon /> },
]

export default function Layout() {
  const location = useLocation()

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            RAG + Local LLM Chatbot
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {menuItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  component={Link}
                  to={item.path}
                  selected={location.pathname === item.path}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  )
}
