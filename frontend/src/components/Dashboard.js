import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Button,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  FormControl,
  InputLabel,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  BarChart as BarChartIcon,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import ws from '../services/websocket';

function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    task_type: 'file_processing',
    parameters: {},
  });
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchTasks();
    fetchAnalytics();
    ws.connect();
    ws.on('task_update', handleTaskUpdate);

    return () => {
      ws.off('task_update', handleTaskUpdate);
    };
  }, []);

  const handleTaskUpdate = (task) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? task : t))
    );
  };

  const fetchTasks = async () => {
    try {
      const response = await api.get('/tasks/');
      setTasks(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/tasks/analytics/');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const handleCreateTask = async () => {
    try {
      await api.post('/tasks/', newTask);
      setCreateDialogOpen(false);
      setNewTask({ title: '', task_type: 'file_processing', parameters: {} });
      fetchTasks();
      fetchAnalytics();
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleRetry = async (taskId) => {
    try {
      await api.post(`/tasks/${taskId}/retry/`);
      fetchTasks();
    } catch (error) {
      console.error('Failed to retry task:', error);
    }
    setAnchorEl(null);
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'default',
      running: 'info',
      success: 'success',
      failed: 'error',
      retrying: 'warning',
    };
    return colors[status] || 'default';
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Task Dashboard</Typography>
        <Box>
          {user?.is_staff && (
            <Button
              startIcon={<BarChartIcon />}
              onClick={() => navigate('/admin')}
              sx={{ mr: 2 }}
            >
              Admin Dashboard
            </Button>
          )}
          <Button variant="outlined" onClick={logout} sx={{ mr: 2 }}>
            Logout
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Task
          </Button>
        </Box>
      </Box>

      {analytics && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Tasks
                </Typography>
                <Typography variant="h4">{analytics.total_tasks}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Success Rate
                </Typography>
                <Typography variant="h4">
                  {analytics.success_rate}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Recent (7 days)
                </Typography>
                <Typography variant="h4">{analytics.recent_tasks}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Running
                </Typography>
                <Typography variant="h4">
                  {analytics.by_status?.running || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Paper>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="h6">Tasks</Typography>
          <IconButton onClick={fetchTasks}>
            <RefreshIcon />
          </IconButton>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.map((task) => (
                <TableRow
                  key={task.id}
                  hover
                  onClick={() => navigate(`/task/${task.id}`)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{task.title}</TableCell>
                  <TableCell>{task.task_type}</TableCell>
                  <TableCell>
                    <Chip
                      label={task.status}
                      color={getStatusColor(task.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ width: 100 }}>
                      <LinearProgress
                        variant="determinate"
                        value={task.progress}
                      />
                      <Typography variant="caption">
                        {task.progress}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    {new Date(task.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <IconButton
                      onClick={(e) => {
                        setAnchorEl(e.currentTarget);
                        setSelectedTask(task);
                      }}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem
          onClick={() => {
            navigate(`/task/${selectedTask?.id}`);
            setAnchorEl(null);
          }}
        >
          View Details
        </MenuItem>
        {selectedTask?.status === 'failed' && (
          <MenuItem onClick={() => handleRetry(selectedTask.id)}>
            Retry
          </MenuItem>
        )}
      </Menu>

      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)}>
        <DialogTitle>Create New Task</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Title"
            margin="normal"
            value={newTask.title}
            onChange={(e) =>
              setNewTask({ ...newTask, title: e.target.value })
            }
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Task Type</InputLabel>
            <Select
              value={newTask.task_type}
              onChange={(e) =>
                setNewTask({ ...newTask, task_type: e.target.value })
              }
            >
              <MenuItem value="file_processing">File Processing</MenuItem>
              <MenuItem value="scraping">Web Scraping</MenuItem>
              <MenuItem value="report_generation">Report Generation</MenuItem>
            </Select>
          </FormControl>
          {newTask.task_type === 'file_processing' && (
            <TextField
              fullWidth
              label="File Path"
              margin="normal"
              placeholder="e.g., /path/to/file.pdf"
              onChange={(e) =>
                setNewTask({
                  ...newTask,
                  parameters: { file_path: e.target.value },
                })
              }
            />
          )}
          {newTask.task_type === 'scraping' && (
            <>
              <TextField
                fullWidth
                label="URL"
                margin="normal"
                placeholder="https://example.com"
                onChange={(e) =>
                  setNewTask({
                    ...newTask,
                    parameters: {
                      ...newTask.parameters,
                      url: e.target.value,
                    },
                  })
                }
              />
              <TextField
                fullWidth
                label="Selectors (JSON)"
                margin="normal"
                placeholder='{"title": "h1", "content": ".content"}'
                onChange={(e) => {
                  try {
                    const selectors = JSON.parse(e.target.value);
                    setNewTask({
                      ...newTask,
                      parameters: {
                        ...newTask.parameters,
                        selectors,
                      },
                    });
                  } catch {}
                }}
              />
            </>
          )}
          {newTask.task_type === 'report_generation' && (
            <FormControl fullWidth margin="normal">
              <InputLabel>Report Type</InputLabel>
              <Select
                onChange={(e) =>
                  setNewTask({
                    ...newTask,
                    parameters: {
                      ...newTask.parameters,
                      report_type: e.target.value,
                    },
                  })
                }
              >
                <MenuItem value="excel">Excel</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
              </Select>
            </FormControl>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateTask} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default Dashboard;

