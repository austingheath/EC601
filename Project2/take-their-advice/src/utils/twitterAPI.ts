import { request } from './request';

const TWITTER_URL = 'https://api.twitter.com/2';
const BEARER_TOKEN = ''; // Not secure. Will need to move Twitter API calls to an API service

export type User = {};

export async function getUser(username: string) {
  const url = TWITTER_URL + `/users/by/username/${username}`;
  return request({ url });
}
