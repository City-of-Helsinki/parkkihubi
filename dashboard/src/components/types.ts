import * as geojson from 'geojson';

export type Point = [number, number];

export interface MapViewport {
    center: Point;
    zoom: number;
    bounds?: {
        neLat: number;
        neLng: number;
        swLat: number;
        swLng: number;
    };
}

export interface Region extends
geojson.Feature<geojson.MultiPolygon, RegionProperties> {
    id: string;
}

export interface RegionProperties {
    name: string;
    capacityEstimate: number;
    areaKm2: number;
    spotsPerKm2: number;
    parkingAreas?: string[];
    parkingCount?: number;
    isSelected?: boolean;
}
