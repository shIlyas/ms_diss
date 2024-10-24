import React from 'react';
import {
  Paper,
  Grid,
  Box,
  Divider,
  TextField,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Fab,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const ChatResultsPanel = ({ result_rubrics, result_tags, messages }) => {
  return (
    <div>
      <Grid item xs={12}>
                  <List >
                    {messages.slice().reverse().map((message, index) => (
                      <ListItem key={index}>
                        <Grid container justifyContent={message.role === 'user' ? 'flex-end' : 'flex-start'}>
                          <Grid item xs={12} sm={message.role === 'user' ? 6 : 8}>
                            <Box
                              sx={{
                                bgcolor: message.role === 'user' ? '#E1F5FE' : '#F1F1F1', // Light blue for user, light gray for others
                                borderRadius: 2,
                                padding: 1,
                                textAlign: message.role === 'user' ? 'right' : 'left',
                              }}
                            >
                              <ListItemText
                                primary={message.message}
                                secondary={new Date(new Date()).toLocaleTimeString()}
                              />
                            </Box>
                          </Grid>
                        </Grid>
                      </ListItem>
                    ))}
                  </List>
                  
                </Grid>
      <Divider style={{ margin: '20px 0' }} />
      {/* Grid for Rubric Questions and Responses */}
      <Grid container spacing={2}>
        {result_rubrics.map((result, index) => (
          <Grid item xs={12} sm={12} key={index}>
            <Accordion>
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls={`panel${index}-content`}
                id={`panel${index}-header`}
              >
                <Typography>{result.question}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography>{result.response}</Typography>
              </AccordionDetails>
            </Accordion>
          </Grid>
        ))}
      </Grid>

      
    
      
    </div>

    
  );
};

export default ChatResultsPanel;
