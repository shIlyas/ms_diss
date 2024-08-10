import React from 'react';
import { List, ListItem, ListItemAvatar, Avatar, ListItemText, Divider } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';

const AssistantList = ({ assistants, onAssistantSelected }) => (
  <List sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
    {assistants.map((assistant) => (
      <React.Fragment key={assistant.id}>
        <ListItem button onClick={() => onAssistantSelected(assistant.id)}>
          <ListItemAvatar>
            <Avatar>
              <PersonIcon />
            </Avatar>
          </ListItemAvatar>
          <ListItemText primary={assistant.name} />
        </ListItem>
        <Divider variant="inset" component="li" />
      </React.Fragment>
    ))}
  </List>
);

export default AssistantList;
