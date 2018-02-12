import { Moment } from 'moment';

import { ParkingList, RegionList, RegionStatsList } from './api/types';
import { MapViewport } from './components/types';

interface CheckExistingLoginAction {
    type: 'CHECK_EXISTING_LOGIN';
}
export function checkExistingLogin(): CheckExistingLoginAction {
    return {type: 'CHECK_EXISTING_LOGIN'};
}

interface ResolveExistingLoginCheckAction {
    type: 'RESOLVE_EXISTING_LOGIN_CHECK';
}
export function resolveExistingLoginCheck(): ResolveExistingLoginCheckAction {
    return {type: 'RESOLVE_EXISTING_LOGIN_CHECK'};
}

interface RequestCodeTokenAction {
    type: 'REQUEST_CODE_TOKEN';
}
export function requestCodeToken(): RequestCodeTokenAction {
    return {type: 'REQUEST_CODE_TOKEN'};
}

interface ReceiveCodeTokenAction {
    type: 'RECEIVE_CODE_TOKEN';
    codeToken: string;
}
export function receiveCodeToken(codeToken: string): ReceiveCodeTokenAction {
    return {type: 'RECEIVE_CODE_TOKEN', codeToken};
}

interface ReceiveCodeTokenFailureAction {
    type: 'RECEIVE_CODE_TOKEN_FAILURE';
    reason: string;
}
export function receiveCodeTokenFailure(
    reason: string
): ReceiveCodeTokenFailureAction {
    return {type: 'RECEIVE_CODE_TOKEN_FAILURE', reason};
}

interface RequestAuthTokenAction {
    type: 'REQUEST_AUTH_TOKEN';
}
export function requestAuthToken(): RequestAuthTokenAction {
    return {type: 'REQUEST_AUTH_TOKEN'};
}

interface ReceiveAuthTokenAction {
    type: 'RECEIVE_AUTH_TOKEN';
    authToken: string;
}
export function receiveAuthToken(authToken: string): ReceiveAuthTokenAction {
    return {type: 'RECEIVE_AUTH_TOKEN', authToken};
}

interface ReceiveAuthTokenFailureAction {
    type: 'RECEIVE_AUTH_TOKEN_FAILURE';
    reason: string;
}
export function receiveAuthTokenFailure(
    reason: string
): ReceiveAuthTokenFailureAction {
    return {type: 'RECEIVE_AUTH_TOKEN_FAILURE', reason};
}

interface LogoutAction {
    type: 'LOGOUT';
}
export function logout(): LogoutAction {
    return {type: 'LOGOUT'};
}

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

interface ReceiveValidParkingsAction {
    type: 'RECEIVE_VALID_PARKINGS';
    data: ParkingList;
    time: Moment;
}
export function receiveValidParkings(
    data: ParkingList,
    time: Moment,
): ReceiveValidParkingsAction {
    return {type: 'RECEIVE_VALID_PARKINGS', data, time};
}

export type Action =
    CheckExistingLoginAction |
    ResolveExistingLoginCheckAction |
    RequestCodeTokenAction |
    ReceiveCodeTokenAction |
    ReceiveCodeTokenFailureAction |
    RequestAuthTokenAction |
    ReceiveAuthTokenAction |
    ReceiveAuthTokenFailureAction |
    LogoutAction |
    SetMapViewportAction |
    SetDataTimeAction |
    SetAutoUpdateAction |
    SetSelectedRegionAction |
    ReceiveRegionStatsAction |
    ReceiveRegionInfoAction |
    ReceiveValidParkingsAction;
