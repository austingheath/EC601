import React from 'react';

import { Box, Typography } from '@mui/material';
import { ThreeCanvas } from './three/ThreeCanvas';

function App() {
  return (
    <Box
      component="div"
      style={{ height: '100vh', width: '100vw', display: 'flex', flexFlow: 'column' }}
    >
      <Box
        component="div"
        style={{
          height: 50,
          backgroundColor: 'blueviolet',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <Typography variant="body1" style={{ marginLeft: 20, color: 'white' }}>
          Robotic Configurator
        </Typography>
      </Box>
      <Box component="div" style={{ flex: 1 }}>
        <ThreeCanvas />
      </Box>
    </Box>
  );
}

export default App;
