import * as geojson from 'geojson';

import { Region, MapViewport } from './components/types';

export type ParkingId = string;
export type Timestamp = number;  // milliseconds since Epoch

export interface RootState {
    auth: AuthenticationState;

    views: ViewState;

    dataTime: Timestamp|null; // milliseconds
    autoUpdate: boolean;

    selectedRegion: string|null;  // regionId

    regions: RegionsMap;

    parkings: ParkingsMap;

    regionUsageHistory: RegionUsageHistory;
    validParkingsHistory: ValidParkingsHistory;
}

export interface AuthenticationState {
    existingLoginChecked?: boolean;
    loggedIn?: boolean;

    codeToken?: string;
    codeTokenFetching?: boolean;
    codeTokenFailure?: string;

    authToken?: string;
    authTokenFetching?: boolean;
    authTokenFailure?: string;
}

export interface ViewState {
    parkingRegionMap: ParkingRegionMapState;
}

export interface ParkingRegionMapState extends MapViewport {
}

export interface RegionsMap {
    [regionId: string]: Region;
}

export interface ParkingsMap {
    [parkingId: string]: Parking;
}

export interface Parking extends
geojson.Feature<geojson.Point, ParkingProperties> {
    id: ParkingId;
    geometry: geojson.Point;
    properties: ParkingProperties;
}

export interface ParkingProperties {
    registrationNumber: string;
    region?: string;
    zone: number;
    terminalNumber?: string;
    operatorName: string;
    timeStart: Timestamp;
    timeEnd: Timestamp|null;
    createdAt: Timestamp;
    modifiedAt: Timestamp;
}

export interface RegionUsageHistory {
    [time: number]: RegionUsageMap;
}

export interface RegionUsageMap {
    [regionId: string]: RegionUsageInfo;
}

export interface RegionUsageInfo {
    parkingCount: number;
}

export interface ValidParkingsHistory {
    [time: number]: ParkingId[];
}
