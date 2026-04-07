import { configureStore } from '@reduxjs/toolkit';

import rootReducer from './reducers';
import { isDev } from './config';

export default function initStore() {
  return configureStore({
    reducer: rootReducer(),
    middleware: (getDefaultMiddleware) => getDefaultMiddleware({
      immutableCheck: false,
    }),
    devTools: isDev,
  });
}
