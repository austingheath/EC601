import React from 'react';

import { useRouteError } from 'react-router-dom';

import { Paper, Typography } from '@mui/material';

import { Centered } from '../components/Centered';

export function ErrorPage() {
  const error = useRouteError() as any;

  return (
    <Centered>
      <Paper>
        <Typography variant="h2">Uh oh...</Typography>
        <Typography variant="caption">Somthing went wrong</Typography>
        <Typography variant="body1">{error.statusText || error.message}</Typography>
      </Paper>
    </Centered>
  );
}
