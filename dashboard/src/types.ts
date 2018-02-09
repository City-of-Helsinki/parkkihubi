import { Region, MapViewport } from './components/types';

export interface RootState {
    views: ViewState;

    dataTime: number|null; // milliseconds
    autoUpdate: boolean;

    selectedRegion: string|null;  // regionId

    regions: RegionsMap;

    regionUsageHistory: RegionUsageHistory;
}

export interface ViewState {
    parkingRegionMap: ParkingRegionMapState;
}

export interface ParkingRegionMapState extends MapViewport {
}

export interface RegionsMap {
    [regionId: string]: Region;
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
