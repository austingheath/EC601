export enum SocketConnectionCloseStatus {
  NormalClosure = 1000,
  EndpointUnavailable = 1001,
  ProtocolError = 1002,
  InvalidMessageType = 1003,
  Empty = 1005,
  ConnectionClosedAbnormally = 1006,
  InvalidPayloadData = 1007,
  PolicyViolation = 1008,
  MessageTooBig = 1009,
  MandatoryExtension = 1010,
  InternalServerError = 1011,
  Unknown = 1012,
}

export class SocketClosure {
  closeStatus: SocketConnectionCloseStatus;
  code: number;
  message: string;
  wasClean: boolean;

  constructor(code: number, message: string, wasClean: boolean) {
    let closeStatus = SocketConnectionCloseStatus.Unknown;
    if (code in SocketConnectionCloseStatus) {
      closeStatus = code;
    }

    this.closeStatus = closeStatus;
    this.code = code;
    this.message = message;
    this.wasClean = wasClean;
  }

  get isError(): boolean {
    return this.closeStatus !== SocketConnectionCloseStatus.NormalClosure;
  }
}
