import * as axios from 'axios';

import { Api } from './index';
import { AuthToken, CodeToken } from './types';

class TokenStorage {
    storeToken(token: string, refreshToken: string | null = null) {
        if (!token) {
            throw new Error('Cannot store empty token');
        }
        localStorage.setItem('AUTH_TOKEN', token);
        localStorage.setItem('AUTH_TOKEN_STORED_AT', Date.now().toString());
        if (refreshToken) {
            localStorage.setItem('REFRESH_TOKEN', refreshToken);
        }
    }

    getToken(): string | null {
        return localStorage.getItem('AUTH_TOKEN');
    }

    getRefreshToken(): string | null {
        return localStorage.getItem('REFRESH_TOKEN');
    }

    clearToken() {
        localStorage.removeItem('AUTH_TOKEN');
        localStorage.removeItem('AUTH_TOKEN_STORED_AT');
        localStorage.removeItem('REFRESH_TOKEN');
    }

    getTokenAge(): number | null {
        const timestampStr = localStorage.getItem('AUTH_TOKEN_STORED_AT');
        if (!this.getToken() || !timestampStr) {
            return null;
        }
        return Date.now() - Number(timestampStr);
    }
}

const tokenStorage = new TokenStorage();

export default class AuthManager {
    /** Maximum age of the token in seconds before it is refreshed. */
    public maxTokenAge: number = 5 * 60 * 1000;  // 5 minutes

    private _api: Api;
    private _axios: axios.AxiosInstance;
    private _authInterceptorId: number | null = null;
    private _tokenRefreshPromise: Promise<AuthToken> | null = null;

    constructor(api: Api, axiosInstance: axios.AxiosInstance) {
        this._api = api;
        this._axios = axiosInstance;
    }

    checkExistingLogin(): Promise<AuthToken|null> {
        return this.refreshLogin().then((authToken) => {
            if (authToken) {
                this._mountAxiosInterceptor();
            }
            return authToken;
        });
    }

    initiateLogin(username: string, password: string): Promise<CodeToken> {
        return this._axios.post<CodeToken>(
            this._api.endpoints.authCodeToken, {username, password}).then(
                (response) => response.data);
    }

    continueLogin(
        codeToken: string, verificationCode: string
    ): Promise<AuthToken> {
        const authTokenUrl = this._api.endpoints.authAuthToken;
        const params = {code_token: codeToken, code: verificationCode};
        return this._axios.post<AuthToken>(authTokenUrl, params).then(
            (response) => {
                const data = response.data;
                tokenStorage.storeToken(
                    data.access || data.token || '',
                    data.refresh || null
                );
                this._ejectAxiosInterceptor();
                this._mountAxiosInterceptor();
                return response.data;
            },
            (error) => {
                tokenStorage.clearToken();
                throw error;
            });
    }

    logout() {
        tokenStorage.clearToken();
        this._ejectAxiosInterceptor();
    }

    refreshLogin(): Promise<AuthToken|null> {
        if (tokenStorage.getToken()) {
            return this._refreshToken();
        }
        return Promise.resolve(null);
    }

    private _mountAxiosInterceptor = () => {
        this._authInterceptorId = (
            this._axios.interceptors.request.use(this._authRequestInterceptor));
    }

    private _ejectAxiosInterceptor = () => {
        if (this._authInterceptorId !== null) {
            this._axios.interceptors.request.eject(this._authInterceptorId);
            this._authInterceptorId = null;
        }
    }

    private _authRequestInterceptor = (request: axios.AxiosRequestConfig) => {
        if ((tokenStorage.getTokenAge() || 0) > this.maxTokenAge) {
            this._refreshToken();
        }
        return {
            ...request,
            headers: {
                ...request.headers,
                'Authorization': `JWT ${tokenStorage.getToken()}`,
            }
        };
    }

    private _refreshToken: (() => Promise<AuthToken>) = () => {
        if (this._tokenRefreshPromise) {
            return this._tokenRefreshPromise;
        }
        const refreshUrl = this._api.endpoints.authRefresh;
        const refresh = tokenStorage.getRefreshToken();
        const data = (refresh) ? {refresh} : {token: tokenStorage.getToken()};
        const promise = this._tokenRefreshPromise = this._axios.post(
            refreshUrl, data).then(
                (response) => {
                    this._tokenRefreshPromise = null;
                    const resp = response.data;
                    tokenStorage.storeToken(resp.access || resp.token || '');
                    return response.data;
                },
                (error) => {
                    this._tokenRefreshPromise = null;
                    tokenStorage.clearToken();
                    throw error;
                });
        return promise;
    }
}
