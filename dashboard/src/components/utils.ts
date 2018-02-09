import { Region } from './types';

export function getRegionName(region: Region) {
    return (region.properties) ? region.properties.name : '';
}
