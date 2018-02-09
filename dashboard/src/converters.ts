/** Functions for converting API data to UI types. */

import * as api from './api/types';
import * as uic from './components/types';
import * as ui from './types';

export function convertRegion(region: api.Region): uic.Region {
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
