import * as _ from 'lodash';
import { combineReducers } from 'redux';

import { Action } from './actions';
import { centerCoordinates } from './config';
import * as conv from './converters';
import {
    AuthenticationState, ParkingRegionMapState, ParkingsMap, RegionsMap,
    RegionUsageHistory, ValidParkingsHistory,
    ViewState } from './types';

// Auth state reducer ////////////////////////////////////////////////

const initialAuthState: AuthenticationState = {
    loggedIn: false,
    existingLoginChecked: false,
};

function auth(
    state: AuthenticationState = initialAuthState,
    action: Action,
): AuthenticationState {
    if (action.type === 'CHECK_EXISTING_LOGIN') {
        return {
            ...state,
            existingLoginChecked: false,
        };
    } else if (action.type === 'RESOLVE_EXISTING_LOGIN_CHECK') {
        return {
            ...state,
            existingLoginChecked: true,
        };
    } else if (action.type === 'REQUEST_CODE_TOKEN') {
        return {
            ...state,
            codeToken: undefined,
            codeTokenFailure: undefined,
            codeTokenFetching: true,
            loggedIn: false,
        };
    } else if (action.type === 'RECEIVE_CODE_TOKEN') {
        return {
            ...state,
            codeToken: action.codeToken,
            codeTokenFetching: false,
        };
    } else if (action.type === 'RECEIVE_CODE_TOKEN_FAILURE') {
        return {
            ...state,
            codeTokenFailure: action.reason,
            codeTokenFetching: false,
        };
    } else if (action.type === 'REQUEST_AUTH_TOKEN') {
        return {
            ...state,
            authToken: undefined,
            authTokenFailure: undefined,
            authTokenFetching: true,
        };
    } else if (action.type === 'RECEIVE_AUTH_TOKEN') {
        return {
            ...state,
            authToken: action.authToken,
            authTokenFetching: false,
            codeToken: undefined,
            loggedIn: true,
        };
    } else if (action.type === 'RECEIVE_AUTH_TOKEN_FAILURE') {
        return {
            ...state,
            authTokenFailure: action.reason,
            authTokenFetching: false,
        };
    } else if (action.type === 'LOGOUT') {
        return {
            ...state,
            codeToken: undefined,
            authToken: undefined,
            loggedIn: false,
        };
    }
    return state;
}

// View state reducers ///////////////////////////////////////////////

const initialParkingRegionMapState: ParkingRegionMapState = {
    bounds: undefined,
    center: centerCoordinates,
    zoom: 12,
};

function parkingRegionMap(
    state: ParkingRegionMapState = initialParkingRegionMapState,
    action: Action
): ParkingRegionMapState {
    if (action.type === 'SET_MAP_VIEWPORT') {
        return {...state, ...action.viewport};
    }
    return state;
}

const views: ((state: ViewState, action: Action) => ViewState) =
    combineReducers({
        parkingRegionMap,
    });

// Helper for creating simple data reducer
function makeReducer<T>(
    actionType: string,
    valueKey: string,
    defaultValue: T,
): ((state: T, action: Action) => T) {
    function reducer(state: T = defaultValue, action: any): T {
        if (action.type === actionType) {
            return action[valueKey];
        }
        return state;
    }
    return reducer;
}

// Data reducers /////////////////////////////////////////////////////

function dataTime(state: number|null = null, action: Action) {
    if (action.type === 'SET_DATA_TIME') {
        return action.time.valueOf();
    }
    return state;
}

const autoUpdate = makeReducer<boolean>('SET_AUTO_UPDATE', 'value', true);
const selectedRegion = makeReducer<string|null>(
    'SET_SELECTED_REGION', 'regionId', null);

function regions(state: RegionsMap = {}, action: Action): RegionsMap {
    if (action.type === 'RECEIVE_REGION_INFO') {
        const newRegions = mapByIdAndApply(
            action.data.features, conv.convertRegion as any);
        return {...state, ...newRegions} as RegionsMap;
    }
    return state;
}

function parkings(state: ParkingsMap = {}, action: Action): ParkingsMap {
    if (action.type === 'RECEIVE_VALID_PARKINGS') {
        const newParkings = mapByIdAndApply(
            action.data.features, conv.convertParking as any);
        return {...state, ...newParkings} as ParkingsMap;
    }
    return state;
}

function regionUsageHistory(
    state: RegionUsageHistory = {},
    action: Action
): RegionUsageHistory {
    if (action.type === 'RECEIVE_REGION_STATS') {
        const timestamp = action.time.valueOf();
        const oldStats = state[timestamp] || {};
        const newStats = mapByIdAndApply(
            action.data.results, conv.convertRegionStats as any);
        return {...state, ...{[timestamp]: {...oldStats, ...newStats}}} as RegionUsageHistory;
    }
    return state;
}

function validParkingsHistory(
    state: ValidParkingsHistory = {},
    action: Action
): ValidParkingsHistory {
    if (action.type === 'RECEIVE_VALID_PARKINGS') {
        const timestamp = action.time.valueOf();
        const oldList = state[timestamp] || [];
        const newList = action.data.features.map(
            (feature: {id: string}) => feature.id);
        return {...state, ...{[timestamp]: [...oldList, ...newList]}};
    }
    return state;
}

interface Mapped<T> {
    [id: string]: T;
}

function mapByIdAndApply<T>(
    objects: ReadonlyArray<{id: string}>,
    converter: ((x: {id: string}) => T)
): Mapped<T> {
    return _.assign({}, ...objects.map((x) => ({[x.id]: converter(x)})));
}

// Root reducer //////////////////////////////////////////////////////

const rootReducer  = () => combineReducers({
        auth,
        views,
        dataTime,
        autoUpdate,
        selectedRegion,
        regions,
        parkings,
        regionUsageHistory,
        validParkingsHistory,
    });

export default rootReducer;
