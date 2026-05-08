// frontend/src/components/ContactsPage.jsx
import React, { useState, useEffect } from 'react';
import {
  Box, Card, Typography, CircularProgress, Alert,
  FormControl, InputLabel, Select, MenuItem, Paper,
  Avatar, Button, Dialog, DialogTitle, DialogContent,
  DialogActions,
  TextField, Switch, FormControlLabel, Stack, IconButton,
  Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Snackbar
} from '@mui/material';
import {
  Business as BusinessIcon,
  People as PeopleIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Star as StarIcon
} from '@mui/icons-material';
import api from '../api';

const ContactsPage = () => {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingContacts, setLoadingContacts] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    mobile: '',
    title: '',
    department: '',
    is_primary: false,
    notes: ''
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchCustomers();
  }, []);

  useEffect(() => {
    if (selectedCustomer) {
      fetchContacts();
    }
  }, [selectedCustomer]);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/crm/customers?limit=100');
      console.log('Customers response:', response.data);
      if (response.data && response.data.data) {
        setCustomers(response.data.data);
      } else {
        setCustomers([]);
      }
    } catch (error) {
      console.error('Error fetching customers:', error);
      showSnackbar(error.response?.data?.detail || error.message || 'Failed to load customers', 'error');
      setCustomers([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchContacts = async () => {
    if (!selectedCustomer) return;
    
    try {
      setLoadingContacts(true);
      const response = await api.get(`/crm/contacts?customer_id=${selectedCustomer.customer_id}`);
      console.log('Contacts response:', response.data);
      setContacts(response.data || []);
    } catch (error) {
      console.error('Error fetching contacts:', error);
      showSnackbar(error.response?.data?.detail || error.message || 'Failed to load contacts', 'error');
      setContacts([]);
    } finally {
      setLoadingContacts(false);
    }
  };

  const handleSubmit = async () => {
    // Validation
    if (!selectedCustomer) {
      showSnackbar('Please select a customer first', 'error');
      return;
    }
    if (!formData.first_name || !formData.first_name.trim()) {
      showSnackbar('First name is required', 'error');
      return;
    }
    if (!formData.last_name || !formData.last_name.trim()) {
      showSnackbar('Last name is required', 'error');
      return;
    }

    setIsSubmitting(true);
    try {
      const contactData = {
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        email: formData.email || null,
        phone: formData.phone || null,
        mobile: formData.mobile || null,
        title: formData.title || null,
        department: formData.department || null,
        is_primary: formData.is_primary,
        notes: formData.notes || null,
        customer_id: selectedCustomer.customer_id
      };

      console.log('Sending contact data:', contactData);
      console.log('Selected customer ID:', selectedCustomer.customer_id);

      let response;
      if (editingContact) {
        response = await api.put(`/crm/contacts/${editingContact.contact_id}`, contactData);
        showSnackbar('Contact updated successfully', 'success');
      } else {
        response = await api.post('/crm/contacts', contactData);
        showSnackbar('Contact added successfully', 'success');
      }
      
      console.log('Response:', response.data);
      
      handleCloseDialog();
      fetchContacts();
    } catch (error) {
      console.error('Error saving contact:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      const errorMsg = error.response?.data?.detail || error.message || 'Error saving contact';
      showSnackbar(errorMsg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (contactId, contactName) => {
    if (window.confirm(`Are you sure you want to delete "${contactName}"? This action cannot be undone.`)) {
      try {
        await api.delete(`/crm/contacts/${contactId}`);
        showSnackbar('Contact deleted successfully', 'success');
        fetchContacts();
      } catch (error) {
        consoleError('Error deleting contact:', error);
        const errorMsg = error.response?.data?.detail || error.message || 'Error deleting contact';
        showSnackbar(errorMsg, 'error');
      }
    }
  };

  const handleOpenDialog = (contact = null) => {
    if (contact) {
      setEditingContact(contact);
      setFormData({
        first_name: contact.first_name || '',
        last_name: contact.last_name || '',
        email: contact.email || '',
        phone: contact.phone || '',
        mobile: contact.mobile || '',
        title: contact.title || '',
        department: contact.department || '',
        is_primary: contact.is_primary || false,
        notes: contact.notes || ''
      });
    } else {
      setEditingContact(null);
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        mobile: '',
        title: '',
        department: '',
        is_primary: false,
        notes: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingContact(null);
  };

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: '#f5f5f5', minHeight: '100vh', p: 3 }}>
      <Card sx={{ borderRadius: 3, overflow: 'hidden' }}>
        {/* Header */}
        <Box sx={{ p: 3, background: 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)', color: 'white' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <PeopleIcon sx={{ fontSize: 30 }} />
            <Box>
              <Typography variant="h5" fontWeight="bold">Contact Management</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Manage contacts for your customers
              </Typography>
            </Box>
          </Box>
        </Box>

        <Box sx={{ p: 3 }}>
          {/* Customer Selection */}
          <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Select Customer
            </Typography>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Choose a customer</InputLabel>
              <Select
                value={selectedCustomer?.customer_id || ''}
                label="Choose a customer"
                onChange={(e) => {
                  const customer = customers.find(c => c.customer_id === e.target.value);
                  console.log('Selected customer:', customer);
                  setSelectedCustomer(customer);
                }}
              >
                {customers.length === 0 ? (
                  <MenuItem disabled>No customers available</MenuItem>
                ) : (
                  customers.map((customer) => (
                    <MenuItem key={customer.customer_id} value={customer.customer_id}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: '#2196f3', width: 32, height: 32 }}>
                          <BusinessIcon sx={{ fontSize: 18 }} />
                        </Avatar>
                        <Box>
                          <Typography variant="body1">{customer.customer_name}</Typography>
                          <Typography variant="caption" color="textSecondary">
                            {customer.email || 'No email'}
                          </Typography>
                        </Box>
                      </Box>
                    </MenuItem>
                  ))
                )}
              </Select>
            </FormControl>
          </Paper>

          {/* Contacts Section */}
          {selectedCustomer ? (
            <Paper sx={{ p: 3, borderRadius: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">
                  Contacts for {selectedCustomer.customer_name}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => handleOpenDialog()}
                  size="small"
                >
                  Add Contact
                </Button>
              </Box>

              {loadingContacts ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : contacts.length === 0 ? (
                <Alert severity="info" sx={{ borderRadius: 2 }}>
                  No contacts found. Click "Add Contact" to get started.
                </Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                      <TableRow>
                        <TableCell><strong>Name</strong></TableCell>
                        <TableCell><strong>Title</strong></TableCell>
                        <TableCell><strong>Contact Info</strong></TableCell>
                        <TableCell><strong>Primary</strong></TableCell>
                        <TableCell><strong>Actions</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {contacts.map((contact) => (
                        <TableRow key={contact.contact_id} hover>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Avatar sx={{ bgcolor: contact.is_primary ? '#4caf50' : '#2196f3' }}>
                                {contact.first_name?.charAt(0)}{contact.last_name?.charAt(0)}
                              </Avatar>
                              <Box>
                                <Typography variant="body1" fontWeight="bold">
                                  {contact.first_name} {contact.last_name}
                                </Typography>
                                {contact.department && (
                                  <Typography variant="caption" color="textSecondary">
                                    {contact.department}
                                  </Typography>
                                )}
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>{contact.title || '-'}</TableCell>
                          <TableCell>
                            {contact.email && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <EmailIcon sx={{ fontSize: 14, color: '#999' }} />
                                <Typography variant="body2">{contact.email}</Typography>
                              </Box>
                            )}
                            {contact.phone && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <PhoneIcon sx={{ fontSize: 14, color: '#999' }} />
                                <Typography variant="body2">{contact.phone}</Typography>
                              </Box>
                            )}
                          </TableCell>
                          <TableCell>
                            {contact.is_primary && (
                              <Chip 
                                label="Primary" 
                                size="small" 
                                color="primary" 
                                icon={<StarIcon sx={{ fontSize: 14 }} />} 
                              />
                            )}
                          </TableCell>
                          <TableCell>
                            <IconButton 
                              size="small" 
                              color="info" 
                              onClick={() => handleOpenDialog(contact)}
                              title="Edit Contact"
                            >
                              <EditIcon />
                            </IconButton>
                            <IconButton 
                              size="small" 
                              color="error" 
                              onClick={() => handleDelete(contact.contact_id, `${contact.first_name} ${contact.last_name}`)}
                              title="Delete Contact"
                            >
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Paper>
          ) : (
            <Alert severity="info" sx={{ borderRadius: 2 }}>
              Please select a customer to view and manage their contacts.
            </Alert>
          )}
        </Box>
      </Card>

      {/* Add/Edit Contact Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#2196f3', color: 'white' }}>
          {editingContact ? 'Edit Contact' : 'Add New Contact'}
        </DialogTitle>
        <DialogContent sx={{ mt: 2, maxHeight: '60vh', overflowY: 'auto' }}>
          <Stack spacing={2}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="First Name *"
                value={formData.first_name}
                onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                required
              />
              <TextField
                fullWidth
                label="Last Name *"
                value={formData.last_name}
                onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                required
              />
            </Box>
            <TextField
              fullWidth
              label="Title/Position"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
            />
            <TextField
              fullWidth
              label="Department"
              value={formData.department}
              onChange={(e) => setFormData({...formData, department: e.target.value})}
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
              />
              <TextField
                fullWidth
                label="Mobile"
                value={formData.mobile}
                onChange={(e) => setFormData({...formData, mobile: e.target.value})}
              />
            </Box>
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_primary}
                  onChange={(e) => setFormData({...formData, is_primary: e.target.checked})}
                />
              }
              label="Primary Contact"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            sx={{ bgcolor: '#2196f3' }}
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : (editingContact ? 'Update' : 'Save')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ContactsPage;