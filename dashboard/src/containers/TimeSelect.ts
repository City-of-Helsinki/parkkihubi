import moment from 'moment';
import { connect } from 'react-redux';

import TimeSelect from '../components/TimeSelect';
import * as dispatchers from '../dispatchers';

const onChange = (time: moment.Moment) => (dispatch) => {
    dispatch(dispatchers.setAutoUpdate(false));
    return dispatch(dispatchers.setDataTime(time));
};

const onAutoUpdateChange = (value) => (dispatch) => dispatch(dispatchers.setAutoUpdate(value));

const mapDispatchToProps = {
    onChange,
    onAutoUpdateChange,
};

const mapStateToProps = (state): any => ({
    value: (state.dataTime) ? moment(state.dataTime) : undefined,
    autoUpdate: state.autoUpdate,
    timeConstraints: {
        minutes: {min: 0, max: 59, step: 5},
        seconds: null
    },
});

export default connect(mapStateToProps, mapDispatchToProps)(TimeSelect);
