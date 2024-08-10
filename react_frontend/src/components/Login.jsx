import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { login,logout } from '../features/authSlice';
import { useNavigate } from 'react-router-dom';
import { Container, Box, Typography, TextField, Button, Link, Alert } from '@mui/material';
import { post } from '../services/apiService';

const LoginPage = () => {
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await post('/login', { email, password });
      console.log('Login successful:', response.data);
      
      // Assuming the response data contains user information and token
      const { token, role, user } = response.data;

      // Dispatch the login action with user data
      dispatch(login({ user, token, role }));

      // Navigate to the home page
      navigate('/home');
    } catch (error) {
      if (error.response && error.response.status === 401) {
        setErrorMessage('Invalid username or password.');
      } else {
        setErrorMessage('An error occurred during login. Please try again.');
      }
    }
  };

  return (
    <Container maxWidth="xs">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          mt: 8,
        }}
      >
        <Typography component="h1" variant="h4" sx={{ color: '#003366', mb: 2 }}>
          Medical Student Learning Portal
        </Typography>
        <Typography component="h2" variant="h6" sx={{ color: '#003366', mb: 4 }}>
          Welcome to your personalized learning experience
        </Typography>
        {errorMessage && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {errorMessage}
          </Alert>
        )}
        <Box component="form" sx={{ width: '100%' }} onSubmit={handleSubmit}>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2, backgroundColor: '#003366', color: '#ffffff' }}
          >
            Login
          </Button>
          <Link href="#" variant="body2" sx={{ display: 'block', mt: 1, color: '#003366' }}>
            Forgot Password?
          </Link>
          <Link href="#" variant="body2" sx={{ display: 'block', mt: 1, color: '#003366' }}>
            New here? Sign Up
          </Link>
        </Box>
        <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 4 }}>
          Your data is secure with us.
        </Typography>
      </Box>
    </Container>
  );
};

export default LoginPage;
