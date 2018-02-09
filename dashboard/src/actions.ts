import { Moment } from 'moment';

import { RegionList, RegionStatsList } from './api/types';
import { MapViewport } from './components/types';

interface SetMapViewportAction {
    type: 'SET_MAP_VIEWPORT';
    viewport: MapViewport;
}
export function setMapViewport(viewport: MapViewport): SetMapViewportAction {
    return {type: 'SET_MAP_VIEWPORT', viewport};
}

interface SetDataTimeAction {
    type: 'SET_DATA_TIME';
    time: Moment;
}
export function setDataTime(time: Moment): SetDataTimeAction {
    return {type: 'SET_DATA_TIME', time};
}

interface SetAutoUpdateAction {
    type: 'SET_AUTO_UPDATE';
    value: boolean;
}
export function setAutoUpdate(value: boolean): SetAutoUpdateAction {
    return {type: 'SET_AUTO_UPDATE', value};
}

interface SetSelectedRegionAction {
    type: 'SET_SELECTED_REGION';
    regionId: string|null;
}
export function setSelectedRegion(regionId: string|null):
SetSelectedRegionAction {
    return {type: 'SET_SELECTED_REGION', regionId};
}

interface ReceiveRegionStatsAction {
    type: 'RECEIVE_REGION_STATS';
    data: RegionStatsList;
    time: Moment;
}
export function receiveRegionStats(
    data: RegionStatsList,
    time: Moment
): ReceiveRegionStatsAction {
    return {type: 'RECEIVE_REGION_STATS', data, time};
}

interface ReceiveRegionInfoAction {
    type: 'RECEIVE_REGION_INFO';
    data: RegionList;
}
export function receiveRegionInfo(data: RegionList): ReceiveRegionInfoAction {
    return {type: 'RECEIVE_REGION_INFO', data};
}

export type Action =
    SetMapViewportAction |
    SetDataTimeAction |
    SetAutoUpdateAction |
    SetSelectedRegionAction |
    ReceiveRegionStatsAction |
    ReceiveRegionInfoAction;
