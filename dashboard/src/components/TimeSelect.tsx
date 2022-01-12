import moment from 'moment';
import DateTime from 'react-datetime';
import * as React from 'react';
import { Button, ButtonGroup, InputGroup } from 'reactstrap';

import 'react-datetime/css/react-datetime.css';

import './TimeSelect.css';
import { Component } from 'react';

export interface Props extends DateTime.DatetimepickerProps {
    autoUpdate?: boolean;
    onAutoUpdateChange?: (newValue: boolean) => void;
}

class AutoUpdatingDatetime extends Component<Props> {
    handleUpdateButtonClick = () => {
        const newAutoUpdate = !this.props.autoUpdate;
        this.setState({autoUpdate: newAutoUpdate} as {}, () => {
            const props = (this.props as Props);
            if (props.onAutoUpdateChange) {
                return props.onAutoUpdateChange(newAutoUpdate);
            }
        });
    }
    render() {
        const icon = this.props.autoUpdate ? 'clock-o' : 'circle-o';
        const iconClass = 'fa fa-' + icon;

        return (
            <div>
                <InputGroup>
                    <DateTime
                        dateFormat="DD.MM.YYYY"
                        timeFormat="HH:mm"
                        value={this.props.value}
                        onChange={this.props.onChange}
                        closeOnSelect
                    />
                    <Button
                        onClick={this.handleUpdateButtonClick}
                        className="update-button"
                        color="info"
                        outline={true}
                        active={this.props.autoUpdate}
                    >
                        <i className={iconClass}/>
                        <span className="text"> Pidä ajan tasalla</span>
                    </Button>
                </InputGroup>
            </div>
        );
    }
}

export default class TimeSelect extends React.Component<Props> {
    datetime?: AutoUpdatingDatetime;

    shiftTime = (minutes: number) => {
        if (this.datetime) {
            const currentTime = this.datetime.props.value;
            if (currentTime != null && moment.isMoment(currentTime)) {
                const newTime = currentTime.clone().add(minutes, 'minutes');
                if (this.props.onChange) {
                    this.props.onChange(newTime);
                }
            }
        }
    }

    render() {
        const timeShiftButton = (label: string, minutes: number) => (
            <Button onClick={() => this.shiftTime(minutes)}>
                {label}
            </Button>);
        return (
            <div className="d-flex justify-content-between">
                <AutoUpdatingDatetime
                    {...this.props}
                    ref={(component: AutoUpdatingDatetime) => {
                        this.datetime = component; }}
                />
                <div>
                    <ButtonGroup className="btn-group-left">
                        {timeShiftButton('-1 vk', -7 * 24 * 60)}
                        {timeShiftButton('-1 pv', -1 * 24 * 60)}
                        {timeShiftButton('-1 t', -60)}
                    </ButtonGroup>
                    {' '}
                    <ButtonGroup className="btn-group-right">
                        {timeShiftButton('+1 t', 60)}
                        {timeShiftButton('+1 pv', 1 * 24 * 60)}
                        {timeShiftButton('+1 vk', 7 * 24 * 60)}
                    </ButtonGroup>
                </div>
            </div>
        );
    }
}
