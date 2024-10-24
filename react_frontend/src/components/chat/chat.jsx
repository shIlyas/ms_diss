// ChatPage.jsx
import React, { useReducer, useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import AssistantList from './assistantList'; // Ensure correct casing for imports
import ChatWindow from './chat_window'; // Ensure correct casing for imports
import { post, put, get, del } from '../../services/apiService'; 
import { useDispatch } from 'react-redux';
import { showSnackbar } from '../../features/snackbarSlice';

const ChatPage = () => {
  const dispatch_global = useDispatch(); // Use Redux dispatch
  const [selectedAssistantId, setSelectedAssistantId] = useState(null);
  const [selectedAssistantName, setSelectedAssistantName] = useState(null);
  const [selectedAssistantRole, setSelectedAssistantRole] = useState(null);
  const [assistants, setAssistants] = useState([]);

  useEffect(() => {
    fetchAssistants();
  }, []);

  const fetchAssistants = async () => {
    try {
      const response = await get('/scenarios');
      setAssistants(response.data);
    } catch (error) {
      console.error('Error fetching assistants:', error);
      dispatch_global(
        showSnackbar({ message: 'Failed to fetch assistants', severity: 'error' })
      );
    }
  };

  const handleAssistantSelected = (id,name,role, tags) => {
    setSelectedAssistantId(id);
    setSelectedAssistantName(name);
    setSelectedAssistantRole(role);
    
  };



  return (
    <Box
      sx={{
        display: 'flex',
        height: '90vh',
        width: '100%',
        bgcolor: '#e5ddd5',
        flexDirection: 'row'
      }}
    >
      <Box
        sx={{
          width: '30vw',
          maxWidth: '30vw',
          bgcolor: '#ffffff',
          boxShadow: 0,
          display: 'flex',
          flexDirection: 'column',
          borderRight: '1px solid #ddd',
          overflowY: 'auto',
          maxHeight: '100vh', // Use full height for the sidebar to enable scrolling
        }}
      >
        <Typography variant="h6" sx={{ p: 2, borderBottom: '1px solid #ddd' }}>
          Scenarios
        </Typography>
    
        <AssistantList
          assistants={assistants}
          selectedAssistantId={selectedAssistantId}
          onAssistantSelected={handleAssistantSelected}
        />
      </Box>
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          width: '70vw',
          height: '70vh'
          
        }}
      >
        <ChatWindow selectedAssistantID={selectedAssistantId}
                    scenarioName = {selectedAssistantName} 
                    scenarioRole = {selectedAssistantRole}
                    />
      </Box>
    </Box>
  );
};

export default ChatPage;
