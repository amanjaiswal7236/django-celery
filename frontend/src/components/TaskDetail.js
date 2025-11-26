import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  LinearProgress,
  Chip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert,
  Grid,
} from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import api from '../services/api';
import ws from '../services/websocket';

function TaskDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTask();
    fetchLogs();
    
    // Subscribe to task updates
    ws.subscribeTask(id);
    ws.on('task_update', handleTaskUpdate);

    return () => {
      ws.unsubscribeTask(id);
      ws.off('task_update', handleTaskUpdate);
    };
  }, [id]);

  const handleTaskUpdate = (updatedTask) => {
    if (updatedTask.id === parseInt(id)) {
      setTask(updatedTask);
      if (updatedTask.status === 'running') {
        fetchLogs();
      }
    }
  };

  const fetchTask = async () => {
    try {
      const response = await api.get(`/tasks/${id}/`);
      setTask(response.data);
    } catch (error) {
      console.error('Failed to fetch task:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await api.get(`/tasks/${id}/logs/`);
      setLogs(response.data);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  };

  const handleRetry = async () => {
    try {
      await api.post(`/tasks/${id}/retry/`);
      fetchTask();
    } catch (error) {
      console.error('Failed to retry task:', error);
    }
  };

  if (loading) {
    return <Container>Loading...</Container>;
  }

  if (!task) {
    return <Container>Task not found</Container>;
  }

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
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/')}
        sx={{ mb: 2 }}
      >
        Back to Dashboard
      </Button>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h4">{task.title}</Typography>
          <Chip
            label={task.status}
            color={getStatusColor(task.status)}
            size="large"
          />
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          Type: {task.task_type} | Created: {new Date(task.created_at).toLocaleString()}
        </Typography>

        {task.status === 'running' && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress variant="determinate" value={task.progress} />
            <Typography variant="body2" sx={{ mt: 1 }}>
              Progress: {task.progress}%
            </Typography>
          </Box>
        )}

        {task.error_message && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {task.error_message}
          </Alert>
        )}

        {task.result && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {task.result}
          </Alert>
        )}

        {task.status === 'failed' && (
          <Button
            variant="contained"
            onClick={handleRetry}
            sx={{ mt: 2 }}
          >
            Retry Task
          </Button>
        )}
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Task Details
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Task ID"
                    secondary={task.id}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Celery Task ID"
                    secondary={task.celery_task_id || 'N/A'}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Retry Count"
                    secondary={`${task.retry_count} / ${task.max_retries}`}
                  />
                </ListItem>
                <Divider />
                {task.started_at && (
                  <>
                    <ListItem>
                      <ListItemText
                        primary="Started At"
                        secondary={new Date(task.started_at).toLocaleString()}
                      />
                    </ListItem>
                    <Divider />
                  </>
                )}
                {task.completed_at && (
                  <>
                    <ListItem>
                      <ListItemText
                        primary="Completed At"
                        secondary={new Date(task.completed_at).toLocaleString()}
                      />
                    </ListItem>
                    <Divider />
                  </>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Task Logs
              </Typography>
              <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                <List>
                  {logs.length === 0 ? (
                    <ListItem>
                      <ListItemText primary="No logs available" />
                    </ListItem>
                  ) : (
                    logs.map((log, index) => (
                      <React.Fragment key={log.id || index}>
                        <ListItem>
                          <ListItemText
                            primary={log.message}
                            secondary={`${log.level} - ${new Date(log.created_at).toLocaleString()}`}
                          />
                        </ListItem>
                        {index < logs.length - 1 && <Divider />}
                      </React.Fragment>
                    ))
                  )}
                </List>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}

export default TaskDetail;

