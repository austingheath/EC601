export type ApiMessageData =
  | {
      type: 'error';
      message: string;
      code: string;
    }
  | {
      type: 'twitterUser';
      id: String;
      username: String;
      name: String;
    };

export type ApiMessage = {
  referenceId: string;
  data: ApiMessageData;
  responseId?: string;
};

export type ClientMessageData =
  | {
      type: 'findUser';
      username: string;
    }
  | {
      type: 'watchTwitterUser';
      username: string;
    };

export type ClientMessage = {
  referenceId: string;
  data: ClientMessageData;
  responseId?: string;
};
