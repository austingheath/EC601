import React, { ChangeEvent, useState } from 'react';

import { Add } from '@mui/icons-material';
import { Box, Button, Chip, MenuItem, TextField, Typography } from '@mui/material';

import { vectorToString } from '../utils/vectorToString';
import { RobotData } from './Configurator';

type StartFormState = {
  currentPoint: string;
  currentOrientation: string;
  points: number[][];
  orientations: number[][];
  euler: string;
  pointError: boolean;
  orientationError: boolean;
};

type StartFormProps = {
  setRobotInfo: (info: RobotData) => void;
};

const eulerOptions = ['XYZ', 'ZYX', 'ZYZ'];

export function StartForm(props: StartFormProps) {
  const [state, setState] = useState<StartFormState>({
    currentPoint: '',
    currentOrientation: '',
    points: [],
    orientations: [],
    euler: 'XYZ',
    pointError: false,
    orientationError: false,
  });

  const { setRobotInfo } = props;

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

  const onSubmit = () => {
    setRobotInfo({
      orientations: state.orientations,
      points: state.points,
      orientationSequence: state.euler,
    });
  };

  return (
    <Box component="div">
      <Typography variant="h3" color="primary">
        Robotic Configurator
      </Typography>
      <Typography variant="caption" color="text.secondary">
        Provide your desired points and orientations. We&apos;ll do the rest.
      </Typography>
      <TextField
        label="Add points"
        onChange={onPointChange}
        value={state.currentPoint}
        size="small"
        fullWidth
        style={{ marginTop: 10 }}
        inputProps={{
          onKeyPress: (event) => {
            if (event.key === 'Enter') {
              onAddPoint();
              event.preventDefault();
            }
          },
        }}
      />
      <Button startIcon={<Add />} variant="outlined" onClick={onAddPoint} style={{ marginTop: 5 }}>
        Add Point
      </Button>
      <Box component="div" mt={2} mb={2}>
        {state.points.map((point, i) => (
          <Chip
            key={i + '' + point}
            label={vectorToString(point)}
            onDelete={() => onRemovePoint(i)}
            style={{ marginRight: 10 }}
          />
        ))}
      </Box>
      <TextField
        label="Add orientations"
        onChange={onOriChange}
        value={state.currentOrientation}
        size="small"
        fullWidth
        inputProps={{
          onKeyPress: (event) => {
            if (event.key === 'Enter') {
              onAddOrientation();
              event.preventDefault();
            }
          },
        }}
      />
      <Button
        startIcon={<Add />}
        variant="outlined"
        onClick={onAddOrientation}
        style={{ marginTop: 5 }}
      >
        Add Orientation
      </Button>
      <Box component="div" mb={2} mt={2}>
        {state.orientations.map((ori, i) => (
          <Chip
            key={i + '' + ori}
            label={vectorToString(ori)}
            onDelete={() => onRemoveOrientation(i)}
            style={{ marginRight: 10 }}
          />
        ))}
      </Box>
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
      <Button
        disabled={state.points.length === 0 && state.orientations.length === 0}
        variant="contained"
        fullWidth
        style={{ marginTop: 20 }}
        onClick={onSubmit}
      >
        Start
      </Button>
    </Box>
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
