import { Dispatch } from 'redux';
import * as moment from 'moment';

import * as actions from './actions';
import api from './api';
import { MapViewport } from './components/types';
import { RootState } from './types';

const updateInterval = 5 * 60 * 1000;  // 5 minutes in ms

export function setMapViewport(viewport: MapViewport) {
    return (dispatch: Dispatch<RootState>) => {
        dispatch(actions.setMapViewport(viewport));
    };
}

export function updateData() {
    return (dispatch: Dispatch<RootState>) => {
        dispatch(setDataTime(moment()));
    };
}

export function setDataTime(time?: moment.Moment) {
    return (dispatch: Dispatch<RootState>, getState: () => RootState) => {
        if (time && typeof time === 'object' && time.isValid()) {
            const {dataTime} = getState();
            const roundedTime = roundTime(time, updateInterval);
            if (!dataTime || roundedTime.valueOf() !== dataTime) {
                dispatch(actions.setDataTime(roundedTime));
                dispatch(fetchRegionStats(roundedTime));
            }
        }
    };
}

function roundTime(time: moment.Moment, precision: number): moment.Moment {
    return moment(Math.floor(time.valueOf() / precision) * precision);
}

export function setAutoUpdate(value: boolean) {
    return (dispatch: Dispatch<RootState>) => {
        dispatch(actions.setAutoUpdate(value));
    };
}

export function setSelectedRegion(regionId: string) {
    return (dispatch: Dispatch<RootState>) => {
        dispatch(actions.setSelectedRegion(regionId));
    };
}

export function fetchRegionStats(time: moment.Moment) {
    return (dispatch: Dispatch<RootState>, getState: () => RootState) => {
        const {regions, regionUsageHistory} = getState();
        const timestamp = time.valueOf();
        if (timestamp in regionUsageHistory) {
            return;
        }
        api.fetchRegionStats(
            time,
            (response) => {
                const results = response.data.results || [];
                const needsRegion = results.some(
                    (x: {id: string}) => (!(x.id in regions)));
                if (needsRegion) {
                    dispatch(fetchRegions());
                }
                dispatch(actions.receiveRegionStats(response.data, time));
            },
            (error) => {
                alert('Region statistics fetch failed: ' + error);
            });
    };
}

export function fetchRegions() {
    return (dispatch: Dispatch<RootState>) => {
        api.fetchRegions(
            (response) => {
                dispatch(actions.receiveRegionInfo(response.data));
            },
            (error) => {
                alert('Region fetch failed: ' + error);
            });
    };
}
