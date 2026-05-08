import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import {
  Box, Grid, Card, CardContent, Typography, Container, LinearProgress,
  Paper, Avatar, useTheme
} from '@mui/material';
import {
  People as PeopleIcon,
  Notes as NotesIcon,
  Business as BusinessIcon,
  ContactPhone as ContactIcon,
  Assignment as AssignmentIcon,
  Star as StarIcon,
  Dashboard as DashboardIcon
} from '@mui/icons-material';

const Dashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    total_customers: 0,
    active_customers: 0,
    total_contacts: 0,
    total_notes: 0,
    total_affiliations: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/crm/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    { title: 'Total Customers', value: dashboardData.total_customers, icon: <PeopleIcon />, color: '#667eea', bg: '#e8eaff' },
    { title: 'Active Customers', value: dashboardData.active_customers, icon: <StarIcon />, color: '#4caf50', bg: '#e8f5e9' },
    { title: 'Total Contacts', value: dashboardData.total_contacts, icon: <ContactIcon />, color: '#ff9800', bg: '#fff3e0' },
    { title: 'Total Notes', value: dashboardData.total_notes, icon: <NotesIcon />, color: '#2196f3', bg: '#e3f2fd' },
    { title: 'Affiliations', value: dashboardData.total_affiliations, icon: <AssignmentIcon />, color: '#9c27b0', bg: '#f3e5f5' },
  ];

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: '#f5f5f5', minHeight: '100vh', py: 3 }}>
      <Container maxWidth="xl">
        {/* Welcome Section */}
        <Paper sx={{ p: 4, mb: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', borderRadius: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ width: 60, height: 60, bgcolor: 'rgba(255,255,255,0.2)' }}>
              <DashboardIcon sx={{ fontSize: 35 }} />
            </Avatar>
            <Box>
              <Typography variant="h4" gutterBottom fontWeight="bold">
                Welcome back, {user?.full_name || user?.email}!
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Here's what's happening with your CRM today.
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={4} lg={2.4} key={index}>
              <Card sx={{ borderRadius: 3, transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-5px)', boxShadow: 6 } }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography color="textSecondary" gutterBottom variant="body2">
                        {stat.title}
                      </Typography>
                      <Typography variant="h3" component="h2" sx={{ fontWeight: 'bold', color: stat.color }}>
                        {stat.value}
                      </Typography>
                    </Box>
                    <Avatar sx={{ bgcolor: stat.bg, color: stat.color, width: 56, height: 56 }}>
                      {stat.icon}
                    </Avatar>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default Dashboard;
