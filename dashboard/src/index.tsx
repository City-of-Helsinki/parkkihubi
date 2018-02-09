import * as Leaflet from 'leaflet';
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as ReactRedux from 'react-redux';
import * as Redux from 'redux';
import * as ReduxLogger from 'redux-logger';
import thunkMiddleware from 'redux-thunk';

// Configure Moment.js to use Finnish locale
import 'moment/locale/fi';

import api from './api';
import * as config from './config';
import App from './containers/App';
import * as dispatchers from './dispatchers';
import rootReducer from './reducers';
import registerServiceWorker from './registerServiceWorker';

import 'bootstrap/dist/css/bootstrap.css';
import 'font-awesome/css/font-awesome.min.css';
import 'leaflet/dist/leaflet.css';
import 'react-select/dist/react-select.css';

import './index.css';

Leaflet.Icon.Default.imagePath =
    '//cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/';

// Construct store with middlewares and enchancers
const middlewares: Redux.Middleware[] = [thunkMiddleware];
if (config.isDev) {
    middlewares.push(ReduxLogger.createLogger());
}
const composeEnhancers = (
    (config.isDev && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__)
    || Redux.compose);
const storeEnhancer = Redux.applyMiddleware(...middlewares);
const store = Redux.createStore(rootReducer, composeEnhancers(storeEnhancer));

// Configure API base URL
api.setBaseUrl(config.apiBaseUrl);

// Check if there is an existing login
store.dispatch(dispatchers.checkExistingLogin());

ReactDOM.render(
    <ReactRedux.Provider store={store}>
        <App />
    </ReactRedux.Provider>,
    document.getElementById('root') as HTMLElement);

registerServiceWorker();
