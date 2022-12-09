import React, { useEffect, useState } from 'react';

import { Box, CircularProgress, Paper, Typography } from '@mui/material';

import { StartForm } from './StartForm';
import { ViewRobot } from './ViewRobot';

export type RobotData = {
  points: number[][];
  orientations: number[][];
  orientationSequence: string;
};

export type ApiResponse =
  | { error: false; robot_dh: number[][]; num_joints: number }
  | { error: true; message: string };

type StartFormState =
  | {
      view: 'start';
    }
  | {
      view: 'loading';
      info: RobotData;
    }
  | {
      view: 'ready';
      response: ApiResponse;
    };

export function Configurator() {
  const [state, setState] = useState<StartFormState>({
    view: 'start',
  });

  useEffect(() => {
    const fetchRobot = async (info: RobotData) => {
      const res = await getRobot(info.points, info.orientations, info.orientationSequence);
      setState((s) => ({ ...s, response: res, view: 'ready' }));
    };

    if (state.view === 'loading') {
      fetchRobot(state.info);
    }
  }, [state]);

  const setRobotInfo = (info: RobotData) => {
    setState({ view: 'loading', info });
  };

  const onReset = () => {
    setState({ view: 'start' });
  };

  let body = <StartForm setRobotInfo={setRobotInfo} />;
  switch (state.view) {
    case 'loading': {
      body = (
        <Box
          component="div"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            flex: 1,
          }}
        >
          <CircularProgress />
          <Typography variant="body1" mt={2}>
            This might take awhile...
          </Typography>
        </Box>
      );
      break;
    }
    case 'ready': {
      body = <ViewRobot apiRes={state.response} onReset={onReset} />;
      break;
    }
  }

  return (
    <Paper
      style={{
        width: 600,
        padding: 20,
        minHeight: 300,
        display: 'flex',
      }}
    >
      {body}
    </Paper>
  );
}

async function getRobot(
  points: number[][],
  orientations: number[][],
  orientationSequence: string,
): Promise<ApiResponse> {
  let response: Response;
  try {
    response = await fetch('http://localhost:5000/api/robots/create', {
      method: 'POST',
      body: JSON.stringify({ points, orientations, orientationSequence }),
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (e) {
    return { error: true, message: (e as Error).message };
  }

  if (response.status > 399) {
    return { error: true, message: `Status was ${response.status}` };
  }

  try {
    const json = await response.json();
    return json as ApiResponse;
  } catch (e) {
    return { error: true, message: (e as Error).message };
  }
}
