import {
  Action,
  applyMiddleware,
  compose,
  createStore,
  Store,
} from 'redux';
import thunk, { ThunkMiddleware } from 'redux-thunk';

import { createLogger } from 'redux-logger';
import { RootState } from './types';
import rootReducer from './reducers';
import * as config from './config';

const middlewares: ThunkMiddleware<RootState, Action>[] = [thunk];
if (config.isDev) {
  middlewares.push(createLogger());
}

const composeEnhancers = (process.env.NODE_ENV === 'development'
    && window
    && (window as any).__REDUX_DEVTOOLS_EXTENSION_COMPOSE__)
  || compose;

export default function initStore(): Store<RootState> {
  return createStore(
    rootReducer(),
    composeEnhancers(
      applyMiddleware(...middlewares),
    ),
  );
}
