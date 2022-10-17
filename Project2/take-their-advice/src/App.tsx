import React from 'react';

import { RouterProvider } from 'react-router-dom';

import { AdviceProvider } from './providers/AdviceProvider';
import { router } from './routing/router';

function App() {
  console.log('hello');
  return (
    <AdviceProvider>
      <RouterProvider router={router} />
    </AdviceProvider>
  );
}

export default App;
