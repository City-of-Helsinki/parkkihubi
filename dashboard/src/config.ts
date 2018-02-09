export const isDev: boolean = (process.env.NODE_ENV === 'development');

export const apiBaseUrl: string = process.env.REACT_APP_API_URL || (
    (isDev)
        ? 'http://localhost:8000/'
        : 'https://api.parkkiopas.fi/');
