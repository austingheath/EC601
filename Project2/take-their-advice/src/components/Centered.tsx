import { Box } from '@mui/material';
import React, { ReactNode } from 'react';

type CenteredProps = {
  children?: ReactNode | ReactNode[];
};

export function Centered(props: CenteredProps) {
  const { children } = props;

  return (
    <Box
      sx={{
        height: '100vw',
        width: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
      }}>
      {children}
    </Box>
  );
}
