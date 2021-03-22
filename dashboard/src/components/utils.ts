import { Region } from './types';

const getRegionName = (region: Region) => ((region.properties) ? region.properties.name : '');
export default getRegionName;
