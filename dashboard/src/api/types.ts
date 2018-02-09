import * as geojson from 'geojson';

//////////////////////////////////////////////////////////////////////
// Primitive types

type Url = string;
type ParkingAreaId = string;
type RegionId = string;

//////////////////////////////////////////////////////////////////////
// Helper interfaces

interface PaginatedList {
    count: number;
    next: Url|null;
    previous: Url|null;
}

// Type of the Features returned by the API
interface ApiFeature<I extends string, P> extends
geojson.Feature<geojson.MultiPolygon, P> {
    type: 'Feature';
    geometry: geojson.MultiPolygon;
    id: I;
    properties: P|null;
}

// Type of the Feature Collections returned by the API
interface ApiFeatureCollection<I extends string, P> extends
geojson.FeatureCollection<geojson.MultiPolygon, P> {
    type: 'FeatureCollection';
    features: Array<ApiFeature<I, P>>;
}

//////////////////////////////////////////////////////////////////////
// Exported API interfaces

export type Region = ApiFeature<RegionId, RegionProperties>;

export interface RegionList extends
ApiFeatureCollection<RegionId, RegionProperties>,
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
