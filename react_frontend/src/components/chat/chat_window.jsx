import React from 'react';
import { Box, Typography } from '@mui/material';

const ChatWindow = ({ threadId }) => {
  return (
    <Box
      sx={{
        flexGrow: 1,
        bgcolor: '#f0f0f0',
        p: 2,
        border: '1px solid blue',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Typography variant="h6" color="textSecondary">
        {threadId ? `Thread ID: ${threadId}` : 'Select a scenario, please'}
      </Typography>
    </Box>
  );
};

export default ChatWindow;
