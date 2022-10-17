import React, { ReactNode, createContext, useCallback, useState, useContext, useMemo } from 'react';
import { API_BASE_URL } from '../utils/api';
import { SocketClosure } from '../utils/ws/SocketClosure';
import { ApiMessage, ClientMessage } from '../utils/messages';
import { useWebSocket } from '../utils/ws/useWebsocket';
import { SocketMessage } from '../utils/ws/SocketMessage';
import { cloneDeep } from 'lodash';

type AdviceProviderProps = {
  children?: ReactNode | ReactNode[];
};

type ApiMessageWithTime = {
  timestamp: Date;
} & ApiMessage;

export type AdviceProviderContext = {
  sendMessage: (m: ClientMessage) => void;
  markMessageRead: (referenceId: string) => void;
  messages: ApiMessageWithTime[];
};

export const AdviceProviderContext = createContext<AdviceProviderContext>({
  sendMessage: () => {},
  markMessageRead: () => {},
  messages: [],
});

export function AdviceProvider(props: AdviceProviderProps) {
  const [messages, setMessages] = useState<ApiMessageWithTime[]>([]);

  const { children } = props;

  const wsOnMessage = useCallback((message: SocketMessage<ApiMessage>) => {
    if (message.error != null || message.data == null || message.data?.data.type === 'error') {
      console.error('Received an error', message.data);
    } else {
      setMessages((m) => {
        const copy = cloneDeep(m);
        copy.push({ ...message.data!, timestamp: message.dateReceived });
        return copy;
      });
    }
  }, []);

  const wsOnClose = useCallback((closure: SocketClosure) => {
    console.error('Socket closed');
  }, []);

  const { sendMessage } = useWebSocket<ApiMessage, ClientMessage>(
    API_BASE_URL + '/ws',
    wsOnMessage,
    wsOnClose
  );

  const markMessageRead = useCallback((referenceId: string) => {
    setMessages((m) => {
      const copy = cloneDeep(m);
      const index = copy.findIndex((mg) => mg.referenceId === referenceId);

      if (index === -1) {
        return m;
      }

      copy.splice(index, 1);

      return copy;
    });
  }, []);

  const contextValue: AdviceProviderContext = useMemo(() => {
    return {
      sendMessage,
      markMessageRead,
      messages,
    };
  }, [sendMessage, messages]);

  return (
    <AdviceProviderContext.Provider value={contextValue}>{children}</AdviceProviderContext.Provider>
  );
}

export const useAdviceProvider = () => useContext(AdviceProviderContext);
