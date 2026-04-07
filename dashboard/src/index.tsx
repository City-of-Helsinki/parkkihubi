import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';

import api from './api';
import initStore from './store';
import * as config from './config';
import App from './containers/App';
import * as dispatchers from './dispatchers';

import 'leaflet/dist/leaflet.css'
import './bootstrap.scss';
import 'font-awesome/css/font-awesome.min.css';
import './index.css';


// Configure API base URL
api.setBaseUrl(config.apiBaseUrl);
const store = initStore();

// Check if there is an existing login
store.dispatch(dispatchers.checkExistingLogin() as any);

const app = (
    <Provider store={store}>
        <App />
    </Provider>
);

const rootElement = document.getElementById('root');
if (!rootElement) {
    throw new Error('Root element #root not found');
}
createRoot(rootElement).render(app);
