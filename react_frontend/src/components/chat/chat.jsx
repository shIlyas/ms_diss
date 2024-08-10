// ChatPage.jsx

import React, { useState } from 'react';
import { Box, Typography } from '@mui/material';
import AssistantList from './assistantList'; // Ensure correct casing for imports
import ChatWindow from './chat_window'; // Ensure correct casing for imports

const assistants = [
  { id: 1, name: 'Assistant 1' },
  { id: 2, name: 'Assistant 2' },
  { id: 3, name: 'Assistant 3' },
  { id: 4, name: 'Assistant 4' },
  { id: 5, name: 'Assistant 5' },
  { id: 6, name: 'Assistant 6' },
  { id: 7, name: 'Assistant 7' },
  { id: 8, name: 'Assistant 8' },
  { id: 9, name: 'Assistant 9' },
  { id: 10, name: 'Assistant 10' },
  { id: 11, name: 'Assistant 11' },
  { id: 12, name: 'Assistant 12' },
  { id: 13, name: 'Assistant 13' },
  { id: 14, name: 'Assistant 14' },
  { id: 15, name: 'Assistant 15' }
];

const ChatPage = () => {
  const [selectedThreadId, setSelectedThreadId] = useState(null);

  const handleAssistantSelected = (id) => {
    setSelectedThreadId(id);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        height: '100vh',
        width: '100vw',
        bgcolor: '#e5ddd5',
      }}
    >
      <Box
        sx={{
          width: 360,
          bgcolor: '#ffffff',
          boxShadow: 1,
          display: 'flex',
          flexDirection: 'column',
          borderRight: '1px solid #ddd',
          overflowY: 'auto',
          maxHeight: '100vh', // Use full height for the sidebar to enable scrolling
        }}
      >
        <Typography variant="h6" sx={{ p: 2, borderBottom: '1px solid #ddd' }}>
          Assistants
        </Typography>
        <AssistantList
          assistants={assistants}
          onAssistantSelected={handleAssistantSelected}
        />
      </Box>
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <ChatWindow threadId={selectedThreadId} />
      </Box>
    </Box>
  );
};

export default ChatPage;
