import React, { useState, useEffect } from 'react';
import {
  Box, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Select, MenuItem, FormControl, InputLabel, Chip, Pagination,
  Typography, CircularProgress, Alert, Snackbar, Avatar, LinearProgress
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon, Business, Email, Phone } from '@mui/icons-material';
import api from '../api';

const CustomerManagement = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [formData, setFormData] = useState({
    customer_name: '',
    email: '',
    phone: '',
    industry: '',
    location: '',
    website: '',
    no_of_employees: '',
    established_year: '',
    status: 'ACTIVE'
  });

  useEffect(() => {
    fetchCustomers();
  }, [page, rowsPerPage]);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * rowsPerPage;
      const response = await api.get(`/crm/customers?skip=${skip}&limit=${rowsPerPage}`);
      
      if (response.data && response.data.data) {
        setCustomers(response.data.data);
        setTotalCount(response.data.pagination?.total || 0);
        setTotalPages(response.data.pagination?.total_pages || 1);
      } else {
        setCustomers([]);
        setTotalCount(0);
        setTotalPages(1);
      }
    } catch (error) {
      console.error('Error fetching customers:', error);
      showSnackbar('Failed to load customers', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!formData.customer_name) {
      showSnackbar('Customer name is required', 'error');
      return;
    }

    setSaving(true);
    try {
      if (editingCustomer) {
        await api.put(`/crm/customers/${editingCustomer.customer_id}`, formData);
        showSnackbar('Customer updated successfully', 'success');
      } else {
        await api.post('/crm/customers', formData);
        showSnackbar('Customer added successfully', 'success');
      }
      handleCloseDialog();
      fetchCustomers();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Error saving customer', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (customerId, customerName) => {
    if (window.confirm(`Are you sure you want to delete "${customerName}"?`)) {
      try {
        await api.delete(`/crm/customers/${customerId}`);
        showSnackbar('Customer deleted successfully', 'success');
        fetchCustomers();
      } catch (error) {
        showSnackbar('Error deleting customer', 'error');
      }
    }
  };

  const handleOpenDialog = (customer = null) => {
    if (customer) {
      setEditingCustomer(customer);
      setFormData({
        customer_name: customer.customer_name || '',
        email: customer.email || '',
        phone: customer.phone || '',
        industry: customer.industry || '',
        location: customer.location || '',
        website: customer.website || '',
        no_of_employees: customer.no_of_employees || '',
        established_year: customer.established_year || '',
        status: customer.status || 'ACTIVE'
      });
    } else {
      setEditingCustomer(null);
      setFormData({
        customer_name: '',
        email: '',
        phone: '',
        industry: '',
        location: '',
        website: '',
        no_of_employees: '',
        established_year: '',
        status: 'ACTIVE'
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingCustomer(null);
  };

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'ACTIVE': return { bg: '#e8f5e9', color: '#4caf50', label: 'Active' };
      case 'INACTIVE': return { bg: '#ffebee', color: '#f44336', label: 'Inactive' };
      case 'SUSPENDED': return { bg: '#fff3e0', color: '#ff9800', label: 'Suspended' };
      default: return { bg: '#f5f5f5', color: '#999', label: status };
    }
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(1);
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
        <Box sx={{ p: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Business sx={{ fontSize: 30 }} />
            <Typography variant="h5" fontWeight="bold">Customer Management</Typography>
          </Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()} sx={{ bgcolor: 'white', color: '#667eea' }}>
            Add Customer
          </Button>
        </Box>

        <TableContainer>
          <Table>
            <TableHead sx={{ bgcolor: '#f5f5f5' }}>
              <TableRow>
                <TableCell><strong>Name</strong></TableCell>
                <TableCell><strong>Email</strong></TableCell>
                <TableCell><strong>Phone</strong></TableCell>
                <TableCell><strong>Industry</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {customers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 5 }}>
                    <Typography color="textSecondary">No customers found.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                customers.map((customer) => {
                  const statusStyle = getStatusColor(customer.status);
                  return (
                    <TableRow key={customer.customer_id} hover>
                      <TableCell><strong>{customer.customer_name}</strong></TableCell>
                      <TableCell>{customer.email || '-'}</TableCell>
                      <TableCell>{customer.phone || '-'}</TableCell>
                      <TableCell>{customer.industry || '-'}</TableCell>
                      <TableCell>
                        <Chip label={statusStyle.label} sx={{ bgcolor: statusStyle.bg, color: statusStyle.color }} size="small" />
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" color="primary" onClick={() => handleOpenDialog(customer)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDelete(customer.customer_id, customer.customer_name)}>
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {totalCount > 0 && (
          <Box sx={{ p: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2" color="textSecondary">Rows per page:</Typography>
              <Select value={rowsPerPage} onChange={handleRowsPerPageChange} size="small" sx={{ minWidth: 70 }}>
                <MenuItem value={5}>5</MenuItem>
                <MenuItem value={10}>10</MenuItem>
                <MenuItem value={25}>25</MenuItem>
                <MenuItem value={50}>50</MenuItem>
              </Select>
              <Typography variant="body2" color="textSecondary">
                {((page - 1) * rowsPerPage) + 1} - {Math.min(page * rowsPerPage, totalCount)} of {totalCount}
              </Typography>
            </Box>
            <Pagination count={totalPages} page={page} onChange={handlePageChange} color="primary" showFirstButton showLastButton />
          </Box>
        )}
      </Paper>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#667eea', color: 'white' }}>
          {editingCustomer ? 'Edit Customer' : 'Add New Customer'}
        </DialogTitle>

         <DialogContent sx={{ mt: 2, maxHeight: '70vh', overflowY: 'auto' }}>  {/* Add this line */}
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
            <TextField fullWidth label="Customer Name *" value={formData.customer_name} onChange={(e) => setFormData({...formData, customer_name: e.target.value})} required />
            <TextField fullWidth label="Email" type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} />
            <TextField fullWidth label="Phone" value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} />
            <TextField fullWidth label="Industry" value={formData.industry} onChange={(e) => setFormData({...formData, industry: e.target.value})} />
            <TextField fullWidth label="Location" value={formData.location} onChange={(e) => setFormData({...formData, location: e.target.value})} />
            <TextField fullWidth label="Website" value={formData.website} onChange={(e) => setFormData({...formData, website: e.target.value})} />
            <TextField fullWidth label="No of Employees" type="number" value={formData.no_of_employees} onChange={(e) => setFormData({...formData, no_of_employees: e.target.value})} />
            <TextField fullWidth label="Established Year" type="number" value={formData.established_year} onChange={(e) => setFormData({...formData, established_year: e.target.value})} />
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select value={formData.status} label="Status" onChange={(e) => setFormData({...formData, status: e.target.value})}>
                <MenuItem value="ACTIVE">Active</MenuItem>
                <MenuItem value="INACTIVE">Inactive</MenuItem>
                <MenuItem value="SUSPENDED">Suspended</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={saving}>
            {saving ? <CircularProgress size={24} /> : (editingCustomer ? 'Update' : 'Save')}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({...snackbar, open: false})}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default CustomerManagement;
