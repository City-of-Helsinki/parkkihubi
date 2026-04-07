import { configureStore } from '@reduxjs/toolkit';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { describe, expect, it } from 'vitest';

import App from './App';
import rootReducer from '../reducers';

function renderAppForLoggedOutUser() {
    const store = configureStore({ reducer: rootReducer() });

    store.dispatch({ type: 'RESOLVE_EXISTING_LOGIN_CHECK' } as any);

    return render(
        <Provider store={store}>
            <App />
        </Provider>
    );
}

function renderAppForLoggedInUser() {
    const store = configureStore({ reducer: rootReducer() });

    store.dispatch({ type: 'RESOLVE_EXISTING_LOGIN_CHECK' } as any);
    store.dispatch({ type: 'SET_AUTO_UPDATE', value: false } as any);
    store.dispatch({
        type: 'RECEIVE_AUTH_TOKEN',
        authToken: 'test-token'
    } as any);

    return render(
        <Provider store={store}>
            <App />
        </Provider>
    );
}

describe('App', () => {
    it('shows login window for logged out users', () => {
        renderAppForLoggedOutUser();

        expect(screen.getByLabelText('Käyttäjätunnus')).toBeTruthy();
        expect(screen.getByLabelText('Salasana')).toBeTruthy();
        expect(screen.getByRole('button', { name: /Seuraava/i })).toBeTruthy();
    });

    it('shows dashboard table and map when logged in', () => {
        const { container } = renderAppForLoggedInUser();

        expect(screen.getByText('Aktiiviset pysäköinnit')).toBeTruthy();
        expect(container.querySelector('.table-card')).toBeTruthy();
        expect(
            container.querySelector('.map-card .leaflet-container')
        ).toBeTruthy();
    });
});
