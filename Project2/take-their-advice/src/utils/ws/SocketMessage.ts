export class SocketMessage<TIncomingMessage> {
  dateReceived: Date;
  data: TIncomingMessage | null;
  error: Error | null;

  private event: MessageEvent<string>;

  constructor(messageEvent: MessageEvent<string>) {
    this.event = messageEvent;
    this.dateReceived = new Date();

    try {
      this.data = JSON.parse(messageEvent.data);
      this.error = null;
    } catch (e) {
      this.data = null;
      this.error = new Error('JSON parsing error');
    }
  }

  get lastEventId(): string {
    return this.event.lastEventId;
  }
}
