import React, { useState, useEffect } from 'react';
import {
  Box, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Select, MenuItem, FormControl, InputLabel, Chip,
  Typography, CircularProgress, Alert, Snackbar, LinearProgress
} from '@mui/material';
import { Delete as DeleteIcon, Add as AddIcon, Business } from '@mui/icons-material';
import api from '../api';

const AffiliationsManagement = () => {
  const [affiliations, setAffiliations] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [formData, setFormData] = useState({
    parent_customer_id: '',
    affiliate_customer_id: '',
    relationship_type: 'AFFILIATE',
    notes: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [affiliationsRes, customersRes] = await Promise.all([
        api.get('/crm/affiliations'),
        api.get('/crm/customers?limit=100')
      ]);
      setAffiliations(affiliationsRes.data || []);
      if (customersRes.data && customersRes.data.data) {
        setCustomers(customersRes.data.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!formData.parent_customer_id || !formData.affiliate_customer_id) {
      showSnackbar('Please select both customers', 'error');
      return;
    }

    if (formData.parent_customer_id === formData.affiliate_customer_id) {
      showSnackbar('Cannot create self affiliation', 'error');
      return;
    }

    try {
      await api.post('/crm/affiliations', formData);
      showSnackbar('Affiliation created successfully', 'success');
      handleCloseDialog();
      fetchData();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Error creating affiliation', 'error');
    }
  };

  const handleDelete = async (affiliationId) => {
    if (window.confirm('Delete this affiliation?')) {
      try {
        await api.delete(`/crm/affiliations/${affiliationId}`);
        showSnackbar('Affiliation deleted successfully', 'success');
        fetchData();
      } catch (error) {
        showSnackbar('Error deleting affiliation', 'error');
      }
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({ parent_customer_id: '', affiliate_customer_id: '', relationship_type: 'AFFILIATE', notes: '' });
  };

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  const getCustomerName = (customerId) => {
    const customer = customers.find(c => c.customer_id === customerId);
    return customer ? customer.customer_name : 'Unknown';
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: '#f5f5f5', minHeight: '100vh', p: 3 }}>
      <Paper sx={{ borderRadius: 3, overflow: 'hidden' }}>
        <Box sx={{ p: 3, background: 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Business sx={{ fontSize: 30 }} />
            <Typography variant="h5" fontWeight="bold">Affiliations Management</Typography>
          </Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenDialog(true)} sx={{ bgcolor: 'white', color: '#9c27b0' }}>
            Add Affiliation
          </Button>
        </Box>

        <TableContainer>
          <Table>
            <TableHead sx={{ bgcolor: '#f5f5f5' }}>
              <TableRow>
                <TableCell><strong>Parent Customer</strong></TableCell>
                <TableCell><strong>Affiliate Customer</strong></TableCell>
                <TableCell><strong>Relationship Type</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {affiliations.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 5 }}>
                    <Typography color="textSecondary">No affiliations found.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                affiliations.map((aff) => (
                  <TableRow key={aff.affiliation_id} hover>
                    <TableCell>{getCustomerName(aff.parent_customer_id)}</TableCell>
                    <TableCell>{getCustomerName(aff.affiliate_customer_id)}</TableCell>
                    <TableCell><Chip label={aff.relationship_type} size="small" /></TableCell>
                    <TableCell><Chip label={aff.status} size="small" color={aff.status === 'ACTIVE' ? 'success' : 'default'} /></TableCell>
                    <TableCell>
                      <IconButton size="small" color="error" onClick={() => handleDelete(aff.affiliation_id)}>
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#9c27b0', color: 'white' }}>Add Affiliation</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Parent Customer</InputLabel>
            <Select value={formData.parent_customer_id} label="Parent Customer" onChange={(e) => setFormData({...formData, parent_customer_id: e.target.value})}>
              {customers.map(c => <MenuItem key={c.customer_id} value={c.customer_id}>{c.customer_name}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Affiliate Customer</InputLabel>
            <Select value={formData.affiliate_customer_id} label="Affiliate Customer" onChange={(e) => setFormData({...formData, affiliate_customer_id: e.target.value})}>
              {customers.map(c => <MenuItem key={c.customer_id} value={c.customer_id}>{c.customer_name}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Relationship Type</InputLabel>
            <Select value={formData.relationship_type} label="Relationship Type" onChange={(e) => setFormData({...formData, relationship_type: e.target.value})}>
              <MenuItem value="AFFILIATE">Affiliate</MenuItem>
              <MenuItem value="SUBSIDIARY">Subsidiary</MenuItem>
              <MenuItem value="PARTNER">Partner</MenuItem>
              <MenuItem value="VENDOR">Vendor</MenuItem>
            </Select>
          </FormControl>
          <TextField fullWidth label="Notes" multiline rows={3} value={formData.notes} onChange={(e) => setFormData({...formData, notes: e.target.value})} sx={{ mt: 2 }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" sx={{ bgcolor: '#9c27b0' }}>Create</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({...snackbar, open: false})}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default AffiliationsManagement;
