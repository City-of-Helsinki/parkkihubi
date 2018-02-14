import * as _ from 'lodash';
import { connect } from 'react-redux';
import { Dispatch } from 'redux';

import ParkingRegionsMap, { Props } from '../components/ParkingRegionsMap';
import { Region, MapViewport } from '../components/types';
import * as dispatchers from '../dispatchers';
import { RootState } from '../types';

function mapStateToProps(state: RootState): Partial<Props> {
    const viewState = state.views.parkingRegionMap;
    return {
        center: viewState.center,
        zoom: viewState.zoom,
        regions: getRegions(state),
    };
}

function getRegions(state: RootState): Region[] {
    const {dataTime, regions, regionUsageHistory} = state;
    const currentRegionUsageMap = (
        (dataTime != null) ? regionUsageHistory[dataTime] : {}) || {};
    const enrichedRegions = _.entries(regions).map(
        ([id, region]: [string, Region]): Region => {
            const properties = (region.properties) ? {
                ...region.properties,
                ...currentRegionUsageMap[id],
                isSelected: (id === state.selectedRegion),
            } : null;
            return {...region, properties};
        });
    return enrichedRegions;
}

function mapDispatchToProps(dispatch: Dispatch<RootState>): Partial<Props> {
    return {
        onRegionClicked: (region: Region) => {
            dispatch(dispatchers.setSelectedRegion(region.id));
        },
        onViewportChanged: (viewport: MapViewport) => (
            dispatch(dispatchers.setMapViewport(viewport))),
    };
}

const ConnectedParkingRegionsMap = connect(
    mapStateToProps, mapDispatchToProps)(ParkingRegionsMap);

export default ConnectedParkingRegionsMap;
