/** Functions for converting API data to UI types. */

import moment from 'moment';

import * as api from './api/types';
import * as ui from './types';

export function convertRegion(region: api.Region): any {
    const p = region.properties;
    const properties = (p) ? {
        name: p.name,
        capacityEstimate: p.capacity_estimate,
        areaKm2: p.area_km2,
        spotsPerKm2: p.spots_per_km2,
        parkingAreas: p.parking_areas,
    } : null;
    return {
        id: region.id,
        type: region.type,
        geometry: region.geometry,
        properties
    };
}

export function convertRegionStats(
    regionStats: api.RegionStats
): ui.RegionUsageInfo {
    return {
        parkingCount: regionStats.parking_count,
    };
}

export function convertParking(parking: api.Parking): ui.Parking {
    const props = parking.properties;
    return {
        id: parking.id,
        geometry: parking.geometry,
        type: parking.type,
        properties: {
            registrationNumber: props.registration_number,
            region: props.region || undefined,
            zone: props.zone,
            terminalNumber: props.terminal_number || undefined,
            operatorName: props.operator_name,
            timeStart: parseTime(props.time_start),
            timeEnd: parseNullableTime(props.time_end) || null,
            createdAt: parseTime(props.created_at),
            modifiedAt: parseTime(props.modified_at),
        },
    };
}

function parseTime(value: string): number {
    return moment(value).valueOf();
}

function parseNullableTime(value?: string|null): number|undefined {
    return (value) ? parseTime(value) : undefined;
}
