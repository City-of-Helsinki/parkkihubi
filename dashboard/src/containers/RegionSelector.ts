import { connect } from 'react-redux';
import * as _ from 'lodash';

import RegionSelector, { Props } from '../components/RegionSelector';
import { Region } from '../components/types';
import getRegionName from '../components/utils';
import * as dispatchers from '../dispatchers';
import { RootState } from '../types';

const getRegionPair = ([id, region]: [string, Region]): [string, string] => [id, getRegionName(region)];

const mapStateToProps = (state: RootState): Props => ({
  regions: _.sortBy(
    _.entries(state.regions).map(getRegionPair),
    [([id, name]: [string, string]) => ([!name, name])]),
  selectedRegion: state.selectedRegion || undefined,
});

const mapDispatchToProps = (dispatch: any): Props => ({
  onRegionChanged: (id: string|null) => dispatch(dispatchers.setSelectedRegion(id)),
});

export default connect(mapStateToProps, mapDispatchToProps)(RegionSelector);
