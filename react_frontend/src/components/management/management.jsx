import React, { useReducer, useState } from 'react';
import {
  Box, Card, CardContent, Typography, Dialog, DialogTitle, DialogContent, DialogActions, Button,
  TextField, IconButton, FormControl, InputLabel, Select, MenuItem, Chip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import { v4 as uuidv4 } from 'uuid'; // For generating unique IDs
import './management.css'; // Import the CSS file

const initialState = {
  id: '',
  name: '',
  role: '',
  description: '',
  enable: true,
  rubrics: [],
  tags: [],
};

const roles = ['Toddler', 'Boy', 'Girl', 'Adult Man', 'Adult Women', 'Elderly Man', 'Elderly Women']; // Add more roles as needed

const reducer = (state, action) => {
  switch (action.type) {
    case 'Set_All':
      return { ...state, ...action.payload };
    case 'SET_ID':
      return { ...state, id: action.payload };
    case 'SET_NAME':
      return { ...state, name: action.payload };
    case 'SET_ROLE':
      return { ...state, role: action.payload };
    case 'SET_DESCRIPTION':
      return { ...state, description: action.payload };
    case 'ADD_RUBRIC':
      return { ...state, rubrics: [...state.rubrics, { id: uuidv4(), question: action.payload }] };
    case 'REMOVE_RUBRIC':
      return { ...state, rubrics: state.rubrics.filter(rubric => rubric.id !== action.payload) };
    case 'ADD_TAG':
      return { ...state, tags: [...state.tags, { id: uuidv4(), tag: action.payload }] };
    case 'REMOVE_TAG':
      return { ...state, tags: state.tags.filter(tag => tag.id !== action.payload) };
    case 'RESET_FORM':
      return { ...initialState, id: '' }; // Ensure a new id is generated each time the form is reset
    default:
      return state;
  }
};

const Management = () => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [open, setOpen] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');
  const [newTag, setNewTag] = useState('');

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setNewQuestion('');
    setNewTag('');
    dispatch({ type: 'RESET_FORM' });
  };

  const handleAddQuestion = () => {
    if (newQuestion.trim() !== '') {
      dispatch({ type: 'ADD_RUBRIC', payload: newQuestion });
      setNewQuestion('');
    }
  };

  const handleAddTag = () => {
    if (newTag.trim() !== '') {
      dispatch({ type: 'ADD_TAG', payload: newTag });
      setNewTag('');
    }
  };

  const handleSubmit = () => {
    // Submit form data to API or state management
    console.log(JSON.stringify(state, null, 2));

    // handleClose();
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', height: '100%', gap: 2 }}>
      <Box className="management-box">
        <Card className="management-card" onClick={handleClickOpen}>
          <CardContent>
            <AddIcon className="management-add-icon" />
            <Typography variant="h5" component="div" gutterBottom>
              Add Assistant
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Dialog for adding/editing assistants */}
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>Add/Edit Assistant</DialogTitle>
        <DialogContent>
          <form className="management-form">
            <TextField
              margin="dense"
              label="Name"
              type="text"
              fullWidth
              variant="outlined"
              value={state.name}
              onChange={(e) => dispatch({ type: 'SET_NAME', payload: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Description"
              type="text"
              fullWidth
              variant="outlined"
              multiline
              rows={4}
              value={state.description}
              onChange={(e) => dispatch({ type: 'SET_DESCRIPTION', payload: e.target.value })}
            />
            <FormControl margin="dense" fullWidth variant="outlined">
              <InputLabel>Role</InputLabel>
              <Select
                value={state.role}
                onChange={(e) => dispatch({ type: 'SET_ROLE', payload: e.target.value })}
                label="Role"
              >
                {roles.map((role) => (
                  <MenuItem key={role} value={role}>
                    {role}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1">Rubrics</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {state.rubrics.map((rubric) => (
                  <Chip
                    key={rubric.id}
                    label={rubric.question}
                    onDelete={() => dispatch({ type: 'REMOVE_RUBRIC', payload: rubric.id })}
                    color="primary"
                    deleteIcon={<RemoveIcon />}
                  />
                ))}
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                <TextField
                  margin="dense"
                  label="New Question"
                  type="text"
                  fullWidth
                  variant="outlined"
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                />
                <IconButton onClick={handleAddQuestion}>
                  <AddIcon />
                </IconButton>
              </Box>
            </Box>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1">Tags</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {state.tags.map((tag) => (
                  <Chip
                    key={tag.id}
                    label={tag.tag}
                    onDelete={() => dispatch({ type: 'REMOVE_TAG', payload: tag.id })}
                    color="primary"
                    deleteIcon={<RemoveIcon />}
                  />
                ))}
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                <TextField
                  margin="dense"
                  label="New Tag"
                  type="text"
                  fullWidth
                  variant="outlined"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                />
                <IconButton onClick={handleAddTag}>
                  <AddIcon />
                </IconButton>
              </Box>
            </Box>
          </form>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSubmit} color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Management;
