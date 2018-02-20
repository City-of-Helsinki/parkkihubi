import * as geojson from 'geojson';

export interface AuthToken {
    token: string;
}

export interface CodeToken {
    token: string;
}

//////////////////////////////////////////////////////////////////////
// Primitive types

type Url = string;
type ParkingAreaId = string;
type RegionId = string;
type ParkingId = string;

//////////////////////////////////////////////////////////////////////
// Helper interfaces

type GObj = geojson.GeometryObject;
type Point = geojson.Point;
type MPoly = geojson.MultiPolygon;

interface PaginatedList {
    count: number;
    next: Url|null;
    previous: Url|null;
}

// Type of the Features returned by the API
interface ApiFeature<G extends GObj, I extends string, P> extends
geojson.Feature<G, P> {
    type: 'Feature';
    geometry: G;
    id: I;
    properties: P;
}

// Type of the Feature Collections returned by the API
interface ApiFeatureCollection<G extends GObj, I extends string, P> extends
geojson.FeatureCollection<G, P> {
    type: 'FeatureCollection';
    features: Array<ApiFeature<G, I, P>>;
}

//////////////////////////////////////////////////////////////////////
// Exported API interfaces

export type Region = ApiFeature<MPoly, RegionId, RegionProperties>;

export interface RegionList extends
ApiFeatureCollection<MPoly, RegionId, RegionProperties>,
PaginatedList {
}

export interface RegionProperties {
    name: string;
    capacity_estimate: number;
    area_km2: number;
    spots_per_km2: number;
    parking_areas: ParkingAreaId[];
}

export interface RegionStatsList extends PaginatedList {
    results: RegionStats[];
}

export interface RegionStats {
    id: RegionId;
    parking_count: number;
}

export interface ParkingList extends
ApiFeatureCollection<Point, ParkingId, ParkingProperties>,
PaginatedList {
}

export type Parking = ApiFeature<Point, ParkingId, ParkingProperties>;

export interface ParkingProperties {
    registration_number: string;
    region?: string|null;
    zone: number;
    terminal_number?: string|null;
    operator_name: string;
    time_start: string;
    time_end?: string|null;
    created_at: string;
    modified_at: string;
}
