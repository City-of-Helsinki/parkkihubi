import * as axios from 'axios';
import { Moment } from 'moment';

import { RegionList, RegionStatsList } from './types';

interface SuccessCallback<T> {
    (response: axios.AxiosResponse<T>): void;
}

interface ErrorHandler {
    (error: axios.AxiosError): void;
}

export class Api {
    public endpoints = {
        regions: '/monitoring/v1/region/',
        regionStats: '/monitoring/v1/region_statistics/',
    };

    private axios: axios.AxiosInstance;

    constructor(baseUrl?: string) {
        this.axios = axios.default.create({baseURL: baseUrl});
    }

    setBaseUrl(baseUrl: string) {
        this.axios.defaults.baseURL = baseUrl;
    }

    fetchRegions(
        callback: SuccessCallback<RegionList>,
        errorHandler: ErrorHandler
    ) {
        this._fetchAllPages(this.endpoints.regions, callback, errorHandler);
    }

    fetchRegionStats(
        time: Moment,
        callback: SuccessCallback<RegionStatsList>,
        errorHandler: ErrorHandler
    ) {
        const timeParam = (time) ? '?time=' + time.toISOString() : '';
        this._fetchAllPages(this.endpoints.regionStats + timeParam,
                            callback, errorHandler);
    }

    private _fetchAllPages(
        url: string,
        callback: SuccessCallback<{}>,
        errorHandler: ErrorHandler
    ) {
        this.axios.get(url)
            .then((response) => {
                callback(response);
                const nextUrl = response.data.next;
                if (nextUrl) {
                    this._fetchAllPages(nextUrl, callback, errorHandler);
                }
            })
            .catch(errorHandler);
    }
}

const api = new Api();

export default api;
