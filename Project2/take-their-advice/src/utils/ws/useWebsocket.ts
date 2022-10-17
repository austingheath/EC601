import React from 'react';
import { SocketClosure, SocketConnectionCloseStatus } from './SocketClosure';
import { SocketMessage } from './SocketMessage';

interface UseWebSocketState<TIncomingMessage> {
  status: WebSocketStatus;
  messageToSend: string | null;
  messageToReceive: SocketMessage<TIncomingMessage> | null;
  socketClosure: SocketClosure | null;
  retryAttempts: number;
}

interface UseWebSocketData<TSendingMessage> {
  status: WebSocketStatus;
  sendMessage: (m: TSendingMessage) => void;
}

export enum WebSocketStatus {
  Connecting,
  Open,
  Closing,
  Closed,
  Retrying,
}

export const useWebSocket = <TIncomingMessage, TSendingMessage>(
  url: string,
  onMessage: (m: SocketMessage<TIncomingMessage>) => void,
  onClose: (m: SocketClosure) => void,
  options?: {
    retryAttempts?: number;
  }
): UseWebSocketData<TSendingMessage> => {
  const [state, setState] = React.useState<UseWebSocketState<TIncomingMessage>>({
    status: WebSocketStatus.Connecting,
    messageToSend: null,
    messageToReceive: null,
    socketClosure: null,
    retryAttempts: 0,
  });

  const socket = React.useRef<WebSocket | null>(null);

  const socketInit = React.useCallback(() => {
    socket.current = new WebSocket(url);

    socket.current.onopen = () => {
      setState((s) => ({
        ...s,
        retryAttempts: 0,
        status: WebSocketStatus.Open,
      }));
    };

    socket.current.onmessage = (event) => {
      setState((s) => ({
        ...s,
        messageToReceive: new SocketMessage(event),
      }));
    };

    socket.current.onclose = (event) => {
      setState((s) => ({
        ...s,
        status: WebSocketStatus.Retrying,
        socketClosure: new SocketClosure(event.code, event.reason, event.wasClean),
      }));
    };

    socket.current.onerror = () => {
      setState((s) => ({
        ...s,
        status: WebSocketStatus.Retrying,
        socketClosure: new SocketClosure(
          SocketConnectionCloseStatus.Unknown,
          'An error occurred',
          false
        ),
      }));
    };
  }, [url]);

  // Setup the socket
  React.useEffect(() => {
    socketInit();

    return () => {
      socket.current?.close();
    };
  }, [socketInit]);

  // Attempt a retry or close
  React.useEffect(() => {
    if (!socket.current) return;

    if (state.status === WebSocketStatus.Retrying) {
      const leftAttempts = options?.retryAttempts ? options.retryAttempts - state.retryAttempts : 0;

      if (leftAttempts === 0) {
        console.error(
          `Could not reconnect after ${options?.retryAttempts ? options?.retryAttempts : 0} retries`
        );
        onClose(state.socketClosure as SocketClosure);
        setState((s) => ({ ...s, status: WebSocketStatus.Closed }));
        return;
      }

      setState((s) => ({
        ...s,
        status: WebSocketStatus.Connecting,
        retryAttempts: s.retryAttempts + 1,
      }));

      socketInit();
    }
  }, [options, state, onClose, socketInit]);

  // send a message
  React.useEffect(() => {
    if (!socket.current) return;

    if (state.messageToSend && state.status !== WebSocketStatus.Retrying) {
      socket.current.send(state.messageToSend);
      setState((s) => ({ ...s, messageToSend: null }));
    }
  }, [state]);

  // receive a message
  React.useEffect(() => {
    if (!socket.current) return;

    if (state.messageToReceive) {
      onMessage(state.messageToReceive);
      setState((s) => ({ ...s, messageToReceive: null }));
    }
  }, [state, onMessage]);

  const sendMessage = (message: TSendingMessage) => {
    setState({
      status: state.status,
      messageToSend: JSON.stringify(message),
      messageToReceive: state.messageToReceive,
      socketClosure: state.socketClosure,
      retryAttempts: state.retryAttempts,
    });
  };

  return {
    sendMessage,
    status: state.status,
  };
};
