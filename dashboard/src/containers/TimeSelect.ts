import * as moment from 'moment';
import { Dispatch } from 'redux';
import { connect } from 'react-redux';

import TimeSelect, { Props } from '../components/TimeSelect';
import * as dispatchers from '../dispatchers';
import { RootState } from '../types';

function mapStateToProps(state: RootState): Partial<Props> {
    return {
        value: (state.dataTime) ? moment(state.dataTime) : undefined,
        autoUpdate: state.autoUpdate,
        timeConstraints: {
            minutes: {min: 0, max: 59, step: 5},
            seconds: undefined
        },
    };
}

function mapDispatchToProps(dispatch: Dispatch<RootState>): Partial<Props> {
    return {
        onChange: (time: moment.Moment) => {
            dispatch(dispatchers.setAutoUpdate(false));
            return dispatch(dispatchers.setDataTime(time));
        },
        onAutoUpdateChange: (value) => {
            return dispatch(dispatchers.setAutoUpdate(value));
        },
    };
}

const ConnectedTimeSelect = connect(
    mapStateToProps, mapDispatchToProps)(TimeSelect);

export default ConnectedTimeSelect;
