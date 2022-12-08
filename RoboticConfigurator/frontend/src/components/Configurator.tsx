import React, { ChangeEvent, useState } from 'react';

import { Box, Button, Chip, MenuItem, Paper, TextField, Typography } from '@mui/material';

type ConfiguratorState = {
  currentPoint: string;
  currentOrientation: string;
  points: number[][];
  orientations: number[][];
  euler: string;
  pointError: boolean;
  orientationError: boolean;
};

const eulerOptions = ['XYZ', 'ZYX', 'ZYZ'];

export function Configurator() {
  const [state, setState] = useState<ConfiguratorState>({
    currentPoint: '',
    currentOrientation: '',
    points: [],
    orientations: [],
    euler: 'XYZ',
    pointError: false,
    orientationError: false,
  });

  const onPointChange = (ev: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setState((s) => ({ ...s, currentPoint: ev.target.value }));
  };

  const onOriChange = (ev: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setState((s) => ({ ...s, currentOrientation: ev.target.value }));
  };

  const onOriRepChange = (ev: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setState((s) => ({ ...s, euler: ev.target.value }));
  };

  const onAddPoint = () => {
    try {
      const v = processVector(state.currentPoint);
      setState((s) => ({ ...s, pointError: false, currentPoint: '', points: [...s.points, v] }));
    } catch (e) {
      setState((s) => ({ ...s, pointError: true }));
    }
  };

  const onAddOrientation = () => {
    try {
      const v = processVector(state.currentOrientation);
      setState((s) => ({
        ...s,
        orientationError: false,
        currentOrientation: '',
        orientations: [...s.orientations, v],
      }));
    } catch (e) {
      setState((s) => ({ ...s, orientationError: true }));
    }
  };

  const onRemovePoint = (index: number) => {
    setState((s) => {
      const copy = [...s.points];
      copy.splice(index, 1);
      return { ...s, points: copy };
    });
  };

  const onRemoveOrientation = (index: number) => {
    setState((s) => {
      const copy = [...s.orientations];
      copy.splice(index, 1);
      return { ...s, orientations: copy };
    });
  };

  return (
    <Paper
      style={{
        width: 600,
        padding: 10,
      }}
    >
      <Typography variant="h3" color="primary">
        Robotic Configurator
      </Typography>
      <Typography variant="caption" color="text.secondary">
        Provide your desired points and orientations. We&apos;ll do the rest.
      </Typography>
      <Box component="div" mt={3} mb={1}>
        {state.points.map((point, i) => (
          <Chip
            key={i + '' + point}
            label={vectorToString(point)}
            onDelete={() => onRemovePoint(i)}
          />
        ))}
      </Box>
      <TextField
        label="Add points"
        onChange={onPointChange}
        value={state.currentPoint}
        size="small"
        fullWidth
        style={{ marginTop: 10 }}
      />
      <Button variant="outlined" onClick={onAddPoint} style={{ marginTop: 5 }}>
        Add Point
      </Button>
      <Box component="div" mb={1}>
        {state.orientations.map((ori, i) => (
          <Chip key={i + '' + ori} label={vectorToString(ori)} onDelete={() => onRemovePoint(i)} />
        ))}
      </Box>
      <TextField
        label="Add orientations"
        onChange={onOriChange}
        value={state.currentOrientation}
        size="small"
        fullWidth
        style={{ marginTop: 10 }}
      />
      <Button variant="outlined" onClick={onAddOrientation} style={{ marginTop: 5 }}>
        Add Orientation
      </Button>

      <Box component="div" mt={3}>
        <TextField
          label="Select orientation representation"
          value={state.euler}
          onChange={onOriRepChange}
          size="small"
          select
          fullWidth
        >
          {eulerOptions.map((e) => (
            <MenuItem key={e} value={e}>
              {e}
            </MenuItem>
          ))}
        </TextField>
      </Box>
      <Button variant="contained" fullWidth style={{ marginTop: 20 }}>
        Submit
      </Button>
    </Paper>
  );
}

function processVector(vector: string) {
  const p = vector.replaceAll('(', '').replaceAll(')', '');
  const ds = p.split(',');

  if (ds.length !== 3) {
    throw new Error('Vector must be formatted properly');
  }

  const result = [];
  try {
    result.push(parseFloat(ds[0]));
    result.push(parseFloat(ds[1]));
    result.push(parseFloat(ds[2]));
  } catch (e) {
    throw new Error('Vector must be formatted properly');
  }

  return result;
}

function vectorToString(vector: number[]) {
  return `(${vector[0]}, ${vector[1]}, ${vector[2]})`;
}
