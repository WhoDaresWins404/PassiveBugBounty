// lib/apiClient.ts
import { ApolloClient, InMemoryCache, HttpLink, split } from '@apollo/client';
import { WebSocketLink } from '@apollo/link-ws';
import { getMainDefinition } from '@apollo/utils';

const httpLink = new HttpLink({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT || 'http://localhost:5000/graphql',
});

// Create subscription link
let wsEndpoint = process.env.NEXT_PUBLIC_WS_ENDPOINT;
if (!wsEndpoint) {
  // Convert http://localhost:5000/graphql → ws://localhost:5000/graphql (for dev)
  const url = new URL(process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT || 'http://localhost:5000/graphql');
  url.protocol = 'ws';
  wsEndpoint = url.toString();
}
const wsLink = new WebSocketLink({
  uri: wsEndpoint,
  options: {
    reconnect: true,
  },
});

// Split links by operation type
const link = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink,
);

export const client = new ApolloClient({
  link,
  cache: new InMemoryCache(),
});
