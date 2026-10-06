import { ApolloClient, HttpLink, InMemoryCache, from } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { LocalStorageWrapper, persistCache } from 'apollo3-cache-persist';
import { getToken } from './auth/token';

const cache = new InMemoryCache();

export const cacheReady = persistCache({
  cache,
  storage: new LocalStorageWrapper(window.localStorage),
});

const authLink = setContext((_, { headers }) => {
  const token = getToken();
  return { headers: { ...headers, ...(token ? { Authorization: `Bearer ${token}` } : {}) } };
});

export const client = new ApolloClient({
  link: from([authLink, new HttpLink({ uri: '/graphql' })]),
  cache,
});
