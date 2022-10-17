import React, { ChangeEvent } from 'react';
import { redirect } from 'react-router-dom';
import { Paper, Typography, TextField, Button } from '@mui/material';
import { Box } from '@mui/system';
import { useAdviceProvider } from '../providers/AdviceProvider';

type LoginPageState = {
  loading: boolean;
  username: string;
  referenceId: string;
  error: boolean;
};

export function LoginPage() {
  const [state, setState] = React.useState<LoginPageState>({
    loading: false,
    username: '',
    referenceId: (Math.random() + 1).toString(36).substring(7),
    error: false,
  });

  const { sendMessage, markMessageRead, messages } = useAdviceProvider();

  React.useEffect(() => {
    if (state.loading) {
      const found = messages.find((m) => m.responseId === state.referenceId);

      if (found != null && found.data.type === 'twitterUser') {
        markMessageRead(found.referenceId);
        redirect('/watch/' + state.username);
      } else if (found != null && found.data.type === 'error') {
        setState((s) => ({
          loading: false,
          username: s.username,
          referenceId: (Math.random() + 1).toString(36).substring(7),
          error: true,
        }));
      }
    }
  }, [state, messages]);

  const onTextInput = (event: ChangeEvent<HTMLInputElement>) => {
    setState((s) => ({ ...s, username: event.target.value }));
  };

  const onButtonPress = () => {
    if (state.username.length > 0) {
      sendMessage({
        referenceId: state.referenceId,
        data: { type: 'findUser', username: state.username },
      });
      setState((s) => ({ ...s, loading: true }));
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexFlow: 'column',
        justifyContent: 'center',
        alignItems: 'center',
      }}>
      <Paper
        sx={{
          width: 350,
        }}>
        <Typography variant="h2">Take Their Advice</Typography>
        <Typography variant="h4"></Typography>
        <TextField placeholder="@username" value={state.username} onChange={onTextInput} />
        <Button onClick={onButtonPress}>Continue</Button>
        {state.error ? <Typography>We couldn't find that user!</Typography> : null}
      </Paper>
    </Box>
  );
}
