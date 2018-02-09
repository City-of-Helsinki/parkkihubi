import * as _ from 'lodash';
import { combineReducers } from 'redux';

import { Action } from './actions';
import * as conv from './converters';
import {
    ParkingRegionMapState, RegionsMap, RegionUsageHistory,
    RootState, ViewState } from './types';

// View state reducers ///////////////////////////////////////////////

const initialParkingRegionMapState: ParkingRegionMapState = {
    bounds: undefined,
    center: [60.17, 24.94],
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
    function reducer(state: T = defaultValue, action: Action): T {
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
            action.data.features, conv.convertRegion);
        return {...state, ...newRegions};
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
            action.data.results, conv.convertRegionStats);
        return {...state, ...{[timestamp]: {...oldStats, ...newStats}}};
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

const rootReducer: ((state: RootState, action: Action) => RootState) =
    combineReducers({
        views,
        dataTime,
        autoUpdate,
        selectedRegion,
        regions,
        regionUsageHistory,
    });

export default rootReducer;
