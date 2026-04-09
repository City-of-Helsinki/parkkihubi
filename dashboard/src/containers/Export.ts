import { connect } from 'react-redux';

import { RootState } from '../types';
import { ExportFilters } from '../api/types'
import Export, { Props } from '../components/Export';
import * as dispatchers from '../dispatchers';

function mapStateToProps(state: RootState): Props {
	return {
		operators: state.operators,
		paymentZones: state.paymentZones,
	};
}

const mapDispatchToProps = (dispatch: any) => ({
	downloadCSV: (filters: ExportFilters) => dispatch(dispatchers.downloadCSV(filters)),
});

export default connect(mapStateToProps, mapDispatchToProps)(Export);
