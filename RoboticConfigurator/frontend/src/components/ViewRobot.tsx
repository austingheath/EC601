import { Error } from '@mui/icons-material';
import { Button, Chip, Typography } from '@mui/material';
import { Box } from '@mui/system';

import { vectorToString } from '../utils/vectorToString';
import { ApiResponse } from './Configurator';

type ViewRobotProps = {
  apiRes: ApiResponse;
  onReset: () => void;
};

export function ViewRobot(props: ViewRobotProps) {
  const { apiRes, onReset } = props;

  if (apiRes.error) {
    return (
      <Box
        component="div"
        style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
        }}
      >
        <Error color="error" fontSize="large" />
        <Typography mt={2}>Something went wrong...</Typography>
        <Typography fontSize={15} color="text.secondary">
          {apiRes.message}
        </Typography>
        <Button onClick={onReset}>Restart</Button>
      </Box>
    );
  }

  return (
    <Box
      component="div"
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <Typography fontSize={25} color="success.main">
        Success!
      </Typography>
      <Typography mt={1} mb={1} color="text.secondary">
        Your robot&apos;s DH parameters [(alpha_i-1, a_i-1, d_i)] should be:
      </Typography>
      <Box component="div">
        {apiRes.robot_dh.map((dh, i) => {
          const copy = [...dh];
          copy[0] = dh[0] * (180 / Math.PI);

          return (
            <Chip
              key={dh + '' + i}
              label={vectorToString(copy)}
              style={{ marginRight: i < apiRes.robot_dh.length - 1 ? 10 : 0 }}
            />
          );
        })}
      </Box>
      <Box component="div">
        <Button style={{ marginTop: 20 }} onClick={onReset}>
          Restart
        </Button>
      </Box>
    </Box>
  );
}
