import { Dispatch } from 'redux';
import { connect } from 'react-redux';
import * as _ from 'lodash';

import RegionSelector, { Props } from '../components/RegionSelector';
import { Region } from '../components/types';
import { getRegionName } from '../components/utils';
import * as dispatchers from '../dispatchers';
import { RootState } from '../types';

function mapStateToProps(state: RootState): Partial<Props> {
    function getRegionPair([id, region]: [string, Region]): [string, string] {
        return [id, getRegionName(region)];
    }

    return {
        regions: _.sortBy(
            _.entries(state.regions).map(getRegionPair),
            [([id, name]: [string, string]) => ([!name, name])]),
        selectedRegion: state.selectedRegion || undefined,
    };
}

function mapDispatchToProps(dispatch: Dispatch<RootState>): Partial<Props> {
    return {
        onRegionChanged: (id: string, name: string) => {
            return dispatch(dispatchers.setSelectedRegion(id));
        },
    };
}

const ConnectedRegionSelector = connect(
    mapStateToProps, mapDispatchToProps)(RegionSelector);

export default ConnectedRegionSelector;
