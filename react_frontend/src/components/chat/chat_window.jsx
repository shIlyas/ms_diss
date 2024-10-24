import React, { useState, useEffect, useRef} from 'react';
import Button from '@mui/material/Button';
import {Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';
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
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SendIcon from '@mui/icons-material/Send';
import ChatResultsDialog from './result_dialog'; 
import BartResults from './bart_results';
import { post, get } from '../../services/apiService'; // Ensure correct import path

const ChatWindow = ({ selectedAssistantID, scenarioName, scenarioRole }) => {
  const [threadID, setThreadID] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const endOfMessagesRef = useRef(null);
  const [results_rubrics, setResultsRubrics] = useState(
        [
        {
          question: 'What is AI?',
          response: 'AI stands for Artificial Intelligence, a branch of computer science focused on creating intelligent machines that can perform tasks that typically require human intelligence.',
        },
        {
          question: 'How does AI work?',
          response: 'AI works by using algorithms to process data, recognize patterns, and make decisions based on that data.',
        },
        {
          question: 'What is Machine Learning?',
          response: 'Machine Learning is a subset of AI that allows computers to learn from data and improve their performance over time without being explicitly programmed.',
        },
        {
          question: 'What are neural networks?',
          response: 'Neural networks are a series of algorithms that attempt to recognize underlying relationships in a set of data through a process that mimics the way the human brain operates.',
        },
        {
          question: 'What is Natural Language Processing (NLP)?',
          response: 'NLP is a field of AI that gives machines the ability to read, understand, and derive meaning from human languages.',
        }
  ]);

  const [results_tags, setResultsTags] = useState(
          [
            { message: 'Message', results:['Yes','Yes','Yes','Yes' ] }
          ]
  );

  const [dialogOpen, setDialogOpen] = useState(false); 
  const [bartDialogOpen, setbartDialogOpen] = useState(false); 
    // Function to openthe dialog
    const bart_evaluation = async () => {
      const pay_load = {
        messages: messages
      };

      
      try {
        const response = await post(`/scenarios/${selectedAssistantID}/tag_evaluation`, pay_load);
    
        if (response.status === 200) {
          // Assuming the response contains 'rubric_responses'
          setResultsTags(response.data.tag_evaluations);
          setbartDialogOpen(true);
        } else {
          console.error('Failed to retrieve tag responses:', response.data);
        }
      } catch (error) {
        console.error('Error retrieving tag responses:', error);
      }
    };

    const openDialog = async () => {
      const pay_load = {
        messages: messages
      };

      try {
        const messageResponse = await post(`/scenarios/${selectedAssistantID}/rubric_responses`, pay_load);
    
        if (messageResponse.status === 200) {
          // Assuming the response contains 'rubric_responses'
          setResultsRubrics(messageResponse.data.rubric_responses);
          setDialogOpen(true);
        } else {
          console.error('Failed to retrieve rubric responses:', messageResponse.data);
        }
      } catch (error) {
        console.error('Error retrieving rubric responses:', error);
      }
      try {
        const response = await post(`/scenarios/${selectedAssistantID}/tag_evaluation`, pay_load);
    
        if (response.status === 200) {
          // Assuming the response contains 'rubric_responses'
          setResultsTags(response.data.tag_evaluations);
          setDialogOpen(true);
        } else {
          console.error('Failed to retrieve tag responses:', response.data);
        }
      } catch (error) {
        console.error('Error retrieving tag responses:', error);
      }
    };

  
    // Function to close the dialog
    const closeBartDialog = () => {
      setbartDialogOpen(false);
    };
    const closeDialog = () => {
      setDialogOpen(false);
    };
  

  useEffect(() => {
    // Scrolls to the last message
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    const fetchThread = async () => {
        try {
          const response = await post('/create_thread', { assistantID: selectedAssistantID });
          setThreadID(response.data.thread_id);
        } catch (error) {
          console.error('Error creating or fetching thread:', error);
        }  
    };

    fetchThread();
  }, [selectedAssistantID]);

  
const fetchMessages = async () => {
    
    if (!threadID) return;
  
    try {
      const payload = {thread_id : threadID };
      const response = await post(`/threads/get_all_messages`, payload);
      const messages = response.data;
  
     
       // Corrected to console.log for debugging
  
      // Check if the last message exists and is not from the system
      if (messages.length > 0) {
        const lastMessage = messages[0];
        if (lastMessage.role !== 'assistant') {
          // Wait for a short period before trying again to avoid spamming the server
          await new Promise(resolve => setTimeout(resolve, 1000));

          return fetchMessages(); // Recursively call fetchMessages again
        }
        setMessages(prevMessages => [...prevMessages, lastMessage]);
      }
  
      // If the last message is from the system or no messages exist, set the messages
      setMessages(messages);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };
  

  useEffect(() => {
    fetchMessages();
  }, [threadID]);

  const handleSendMessage = async () => {

    if (newMessage.trim() === '') return;
  
    try {
      const messagePayload = {
        assistant_id: selectedAssistantID,
        thread_id: threadID,
        role: 'user',  // Assuming the role is 'user'
        content: newMessage,
      };
      console.log(messagePayload)
  
      // Step 1: Send the user's message to the Flask backend
      const messageResponse = await post('/threads/send_message', messagePayload);
  
      if (messageResponse.status === 200) {
        setNewMessage(''); // Clear the input field
  
        // Step 2: Run the assistant on the thread
        const runPayload = {
          assistant_id: selectedAssistantID,
          thread_id: threadID,
        };
  
        const runResponse = await post('/threads/run', runPayload);
  
        if (runResponse.status === 200) {
          // Step 3: Fetch the messages again after running the assistant
            setMessages(prevMessages => [
              
              {
                role: 'user',
                message: newMessage,
                created_at: new Date(),
              },
              ...prevMessages
            ]);
          fetchMessages();
        } else {
          console.error('Error running assistant:', runResponse.data);
        }
      } else {
        console.error('Error sending message:', messageResponse.data);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };
  

  return (
    <Box >
      
      <Grid container component={Paper} style={{ width: '100%'}}>
      
        <Grid item container xs={12}
              alignItems="center"
              sx={{ display: 'flex', justifyContent: 'space-between', padding: '10px' }}>
            <Box xs = {6} sx={{ display: 'flex', alignItems: 'center', width: '50%' }}>
              <Avatar alt="User Avatar" src={`${process.env.PUBLIC_URL}/avatars/${scenarioRole}.webp`}>
                <PersonIcon />
              </Avatar>
              <Typography variant="p" style={{ paddingLeft: '10px' }}>
                {scenarioName}
              </Typography>
            </Box>
            <Button xs = {3} onClick={bart_evaluation} variant="contained" sx={{ backgroundColor: 'orange', color: 'white', marginLeft: 'auto' }}>
              Bart Assessment
            </Button>
            <Button xs = {3} onClick={openDialog} variant="contained" sx={{ backgroundColor: 'orange', color: 'white', marginLeft: 'auto' }}>
              GPT Assessment
            </Button>
          </Grid>
              <Divider style={{ width: '100%' }} />
                <Grid item xs={12}>
                  <List style={{ height: '60vh', overflowY: 'auto' }}>
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
                    <div ref={endOfMessagesRef} />
                  </List>
                  <Divider />
                  <Grid container style={{ padding: '20px' }}>
                    <Grid item xs={11}>
                      <TextField
                        label="Type Something"
                        fullWidth
                        value={newMessage}
                        disabled={threadID === null}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleSendMessage();
                          }
                        }}
                        onChange={(e) => setNewMessage(e.target.value)}
                      />
                    </Grid>
                    <Grid item xs={1} align="right">
                      <Fab color="primary" aria-label="send" onClick={handleSendMessage}>
                        <SendIcon />
                      </Fab>
                    </Grid>
                  </Grid>
                </Grid>
      </Grid>

      <Dialog open={dialogOpen} onClose={closeDialog} fullWidth>
              <DialogTitle>GPT Assessment</DialogTitle>
              <DialogContent>
                <ChatResultsDialog result_rubrics={results_rubrics} result_tags={results_tags} messages={messages}/>
              </DialogContent>
              <DialogActions>
                <Button onClick={closeDialog} color="primary">
                  Close
                </Button>
                <Button onClick={() => window.print()} color="primary">
                  Print
                </Button>
              </DialogActions>
      </Dialog>


      <Dialog
        open={bartDialogOpen}
        onClose={closeDialog}
        fullWidth
        maxWidth={false} // Prevents Material-UI from limiting the dialog size to pre-defined values (e.g., 'sm', 'md', 'lg')
        sx={{
          width: '75%',
          height: '60%',
          maxWidth: 'none',
          
          margin: 'auto', // Horizontally center the dialog
          position: 'absolute', // Use absolute positioning to control vertical placement
          top: '20%', // Adjust top to vertically position
          left: '50%', // Move dialog to center horizontally
          transform: 'translateX(-50%)' // Properly center horizontally by moving left half of its width
        }}
      >
              <DialogTitle>BART Assessment</DialogTitle>
              <DialogContent>
                <BartResults result_rubrics={results_rubrics} result_tags={results_tags} messages={messages}/>
              </DialogContent>
              <DialogActions>
                <Button onClick={closeBartDialog} color="primary">
                  Close
                </Button>
                <Button onClick={() => window.print()} color="primary">
                  Print
                </Button>
              </DialogActions>
      </Dialog>

    </Box>
  );
};

export default ChatWindow;
