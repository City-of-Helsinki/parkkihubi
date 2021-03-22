import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';

import api from './api';
import initStore from './store';
import * as config from './config';
import App from './containers/App';
import * as dispatchers from './dispatchers';
import reportWebVitals from './reportWebVitals';

import 'leaflet/dist/leaflet.css'
import 'bootstrap/dist/css/bootstrap.css';
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

ReactDOM.render(app, document.getElementById('root'));
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
