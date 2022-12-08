import React from 'react';

import { Box } from '@mui/material';

import { Configurator } from './components/Configurator';

function App() {
  return (
    <Box
      component="div"
      style={{
        height: '100vh',
        width: '100vw',
        display: 'flex',
        flexFlow: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Configurator />
    </Box>
  );
}

export default App;
