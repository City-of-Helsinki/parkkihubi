import * as moment from 'moment';
import * as ReactDatetime from 'react-datetime';
import CalendarContainer from 'react-datetime/src/CalendarContainer';
import * as React from 'react';
import { Button, ButtonGroup, Input, InputGroup,
         InputGroupButton, Row, Col } from 'reactstrap';

import 'react-datetime/css/react-datetime.css';

import './TimeSelect.css';

export interface Props extends ReactDatetime.DatetimepickerProps {
    autoUpdate?: boolean;
    onAutoUpdateChange?: (newValue: boolean) => void;
}

// The implementation of AutoUpdatingDatetime needs to know more
// internals of the ReactDatetime than is exported by the TS type
// definitions.  Make them visible by definining a couple extended
// interfaces.
interface ExtendedReactDatetime extends ReactDatetime {
    getInitialState: () => {};
    getStateFromProps: (props: Props) => {};
    onInputKey: (event: React.KeyboardEvent<HTMLInputElement>) => void;
    onInputChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
    handleClickOutside: () => void;
}
interface ReactDatetimeInt {
    openCalendar?: (event: React.SyntheticEvent<HTMLElement>) => void;
    onInputChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const ReactDatetimeProto = ReactDatetime.prototype as ExtendedReactDatetime;

class AutoUpdatingDatetime extends ReactDatetime {
    static defaultProps = {
        className: '',
        defaultValue: '',
        inputProps: {},
        input: true,
        onFocus: () => undefined,
        onBlur: () => undefined,
        onChange: () => undefined,
        onViewModeChange: () => undefined,
        timeFormat: true,
        timeConstraints: {},
        dateFormat: true,
        strictParsing: true,
        closeOnSelect: false,
        closeOnTab: true,
        utc: false,

        onAutoUpdateChange: (newValue: boolean) => undefined,
        autoUpdate: false,
    };

    getInitialState() {
        return {
            ...ReactDatetimeProto.getInitialState.call(this),
            autoUpdate: AutoUpdatingDatetime.defaultProps.autoUpdate,
        };
    }

    getStateFromProps = (props: Props) => (
        this.getStateFromPropsOverride(props))

    getStateFromPropsOverride(props: Props) {
        return {
            ...ReactDatetimeProto.getStateFromProps.call(this, props),
            autoUpdate: props.autoUpdate,
        };
    }

    handleUpdateButtonClick = (
        event: React.SyntheticEvent<HTMLButtonElement>
    ) => {
        const newAutoUpdate = !(this.state as {autoUpdate?: boolean}).autoUpdate;
        this.setState({autoUpdate: newAutoUpdate} as {}, () => {
            const props = (this.props as Props);
            if (props.onAutoUpdateChange) {
                return props.onAutoUpdateChange(newAutoUpdate);
            }
        });
    }

    handleInputKey(event: React.KeyboardEvent<HTMLInputElement>) {
        if (event.key === 'Enter') {
            const {inputValue, inputFormat} = this.state;
            // Parse the input value to moment object in non-strict mode
            const time = moment(inputValue, inputFormat, false);
            if (time.isValid()) {
                this.setTimeValue(time);
            }
        }
        ReactDatetimeProto.onInputKey.call(this, event);
    }

    setTimeValue(time: moment.Moment) {
        const event = {target: {value: time.format(this.state.inputFormat)}};
        ReactDatetimeProto.onInputChange.call(this, event);
    }

    render() {
        let className = 'rdt' + ((this.state.open) ? ' rdtOpen' : '');
        const icon = ((this.state as Props).autoUpdate) ? 'clock-o' : 'circle-o';
        const iconClass = 'fa fa-' + icon;
        const inputProps = {
            key: 'i',
            type: 'text' as 'text',
            className: 'form-control',
            onFocus: (this as ReactDatetimeInt).openCalendar,
            onChange: (this as ReactDatetimeInt).onInputChange,
            onKeyDown: this.handleInputKey.bind(this),
            value: this.state.inputValue,
        };

        const getComponentProps = (this as {getComponentProps?: () => {}}).getComponentProps;
        const componentProps = (getComponentProps) ? getComponentProps() : {};
        const handleClickOutside = ReactDatetimeProto.handleClickOutside.bind(this);

        return (
            <div className={className}>
                <InputGroup>
                    <Input {...inputProps}/>
                    <div key="dt" className="rdtPicker">
                        <CalendarContainer
                            view={(this.state as {currentView?: string}).currentView || ''}
                            viewProps={componentProps}
                            onClickOutside={handleClickOutside}
                        />
                    </div>
                    <InputGroupButton>
                        <Button
                            onClick={this.handleUpdateButtonClick}
                            className="update-button"
                            color="info"
                            outline={true}
                            active={(this.state as {autoUpdate?: boolean}).autoUpdate}
                        >
                            <i className={iconClass}/>
                            <span className="text"> Pidä ajan tasalla</span>
                        </Button>
                    </InputGroupButton>
                </InputGroup>
            </div>
        );
    }
}

export default class TimeSelect extends React.Component<Props> {
    datetime?: AutoUpdatingDatetime;

    shiftTime(minutes: number) {
        if (this.datetime) {
            const currentTime = this.datetime.props.value;
            if (currentTime != null && moment.isMoment(currentTime)) {
                const newTime = currentTime.clone().add(minutes, 'minutes');
                this.datetime.setTimeValue(newTime);
            }
        }
    }

    render() {
        const timeShiftButton = (label: string, minutes: number) => (
            <Button onClick={this.shiftTime.bind(this, minutes)}>
                {label}
            </Button>);
        const datetimeProps = this.props;
        return (
            <div className="time-select text-center">
                <Row className="justify-content-center">
                    <Col className="justify-content-center">
                        <AutoUpdatingDatetime
                            {...datetimeProps}
                            ref={(component: AutoUpdatingDatetime) => {
                                    this.datetime = component; }}
                        />
                    </Col>
                </Row>
                <Row>
                    <Col className="shift-buttons">
                        <ButtonGroup size="sm" className="btn-group-left">
                            {timeShiftButton('-1 vk', -7 * 24 * 60)}
                            {timeShiftButton('-1 pv', -1 * 24 * 60)}
                            {timeShiftButton('-1 t', -60)}
                        </ButtonGroup>
                        <ButtonGroup size="sm" className="btn-group-right">
                            {timeShiftButton('+1 t', 60)}
                            {timeShiftButton('+1 pv', 1 * 24 * 60)}
                            {timeShiftButton('+1 vk', 7 * 24 * 60)}
                        </ButtonGroup>
                    </Col>
                </Row>
            </div>
        );
    }
}
